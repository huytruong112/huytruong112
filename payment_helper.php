<?php
/**
 * Payment Helper - Xử lý logic thanh toán tự động
 * File này chứa các hàm helper để xử lý thanh toán tự động
 */

require_once 'db.php';
require_once 'config_payment.php';

class PaymentHelper {
    private $conn;
    
    public function __construct($db_connection) {
        $this->conn = $db_connection;
    }
    
    /**
     * Xử lý thanh toán tự động khi nhận được thông tin giao dịch
     * 
     * @param string $unique_code Mã giao dịch (nội dung chuyển khoản)
     * @param float $amount Số tiền nhận được
     * @param string $transaction_ref Mã tham chiếu từ ngân hàng
     * @param array $extra_data Dữ liệu bổ sung
     * @return array Kết quả xử lý
     */
    public function processAutoPayment($unique_code, $amount, $transaction_ref = '', $extra_data = []) {
        try {
            // Log bắt đầu xử lý
            $this->logPayment("Bắt đầu xử lý thanh toán tự động cho mã: $unique_code, số tiền: $amount");
            
            // 1. Tìm giao dịch pending trong database
            $stmt = $this->conn->prepare("
                SELECT transaction_id, user_id, amount_paid, status, transaction_date 
                FROM transactions 
                WHERE unique_code = ? AND status = 'pending'
                LIMIT 1
            ");
            $stmt->bind_param("s", $unique_code);
            $stmt->execute();
            $result = $stmt->get_result();
            $transaction = $result->fetch_assoc();
            
            if (!$transaction) {
                $this->logPayment("Không tìm thấy giao dịch pending với mã: $unique_code");
                return [
                    'success' => false,
                    'message' => 'Không tìm thấy giao dịch hoặc giao dịch đã được xử lý'
                ];
            }
            
            // 2. Kiểm tra số tiền có khớp không (chấp nhận sai số nhỏ)
            $expected_amount = (float)$transaction['amount_paid'];
            $received_amount = (float)$amount;
            
            if (abs($expected_amount - $received_amount) > 1) { // Cho phép sai số 1 VND
                $this->logPayment("Số tiền không khớp. Mong đợi: $expected_amount, nhận được: $received_amount");
                return [
                    'success' => false,
                    'message' => 'Số tiền không khớp với yêu cầu nạp tiền'
                ];
            }
            
            // 3. Bắt đầu transaction để đảm bảo tính toàn vẹn dữ liệu
            $this->conn->begin_transaction();
            
            try {
                // 4. Cập nhật trạng thái giao dịch thành 'success'
                $stmt_update = $this->conn->prepare("
                    UPDATE transactions 
                    SET status = 'success', 
                        updated_at = NOW(),
                        bank_transaction_ref = ?
                    WHERE transaction_id = ? AND status = 'pending'
                ");
                $stmt_update->bind_param("si", $transaction_ref, $transaction['transaction_id']);
                $stmt_update->execute();
                
                if ($stmt_update->affected_rows === 0) {
                    throw new Exception("Không thể cập nhật trạng thái giao dịch");
                }
                
                // 5. Cộng tiền vào tài khoản user
                $stmt_balance = $this->conn->prepare("
                    UPDATE users 
                    SET balance = balance + ? 
                    WHERE id = ?
                ");
                $stmt_balance->bind_param("di", $received_amount, $transaction['user_id']);
                $stmt_balance->execute();
                
                if ($stmt_balance->affected_rows === 0) {
                    throw new Exception("Không thể cập nhật số dư user");
                }
                
                // 6. Ghi log chi tiết giao dịch
                $this->insertPaymentLog(
                    $transaction['transaction_id'],
                    $transaction['user_id'],
                    $unique_code,
                    $received_amount,
                    $transaction_ref,
                    'success',
                    $extra_data
                );
                
                // 7. Commit transaction
                $this->conn->commit();
                
                $this->logPayment("Xử lý thanh toán thành công cho mã: $unique_code");
                
                // 8. Gửi thông báo email (nếu bật)
                if (EMAIL_NOTIFICATION_ENABLED) {
                    $this->sendPaymentNotification($transaction['user_id'], $received_amount);
                }
                
                return [
                    'success' => true,
                    'message' => 'Thanh toán thành công',
                    'transaction_id' => $transaction['transaction_id'],
                    'user_id' => $transaction['user_id'],
                    'amount' => $received_amount
                ];
                
            } catch (Exception $e) {
                // Rollback nếu có lỗi
                $this->conn->rollback();
                $this->logPayment("Lỗi khi xử lý thanh toán: " . $e->getMessage());
                throw $e;
            }
            
        } catch (Exception $e) {
            $this->logPayment("Exception: " . $e->getMessage());
            return [
                'success' => false,
                'message' => 'Lỗi xử lý thanh toán: ' . $e->getMessage()
            ];
        }
    }
    
    /**
     * Kiểm tra và hủy các giao dịch timeout
     */
    public function cancelTimeoutTransactions() {
        try {
            $timeout = TRANSACTION_TIMEOUT;
            $stmt = $this->conn->prepare("
                UPDATE transactions 
                SET status = 'cancelled' 
                WHERE status = 'pending' 
                AND TIMESTAMPDIFF(SECOND, transaction_date, NOW()) > ?
            ");
            $stmt->bind_param("i", $timeout);
            $stmt->execute();
            
            $cancelled_count = $stmt->affected_rows;
            
            if ($cancelled_count > 0) {
                $this->logPayment("Đã hủy $cancelled_count giao dịch timeout");
            }
            
            return $cancelled_count;
        } catch (Exception $e) {
            $this->logPayment("Lỗi khi hủy giao dịch timeout: " . $e->getMessage());
            return 0;
        }
    }
    
    /**
     * Lấy danh sách giao dịch pending cần kiểm tra
     */
    public function getPendingTransactions() {
        try {
            $stmt = $this->conn->query("
                SELECT transaction_id, user_id, amount_paid, unique_code, transaction_date 
                FROM transactions 
                WHERE status = 'pending' 
                ORDER BY transaction_date DESC
            ");
            
            return $stmt->fetch_all(MYSQLI_ASSOC);
        } catch (Exception $e) {
            $this->logPayment("Lỗi khi lấy giao dịch pending: " . $e->getMessage());
            return [];
        }
    }
    
    /**
     * Ghi log chi tiết thanh toán vào database
     */
    private function insertPaymentLog($transaction_id, $user_id, $unique_code, $amount, $bank_ref, $status, $extra_data) {
        try {
            // Tạo bảng payment_logs nếu chưa có
            $this->conn->query("
                CREATE TABLE IF NOT EXISTS payment_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    transaction_id INT,
                    user_id INT,
                    unique_code VARCHAR(50),
                    amount DECIMAL(15,2),
                    bank_transaction_ref VARCHAR(100),
                    status VARCHAR(50),
                    extra_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_transaction (transaction_id),
                    INDEX idx_user (user_id),
                    INDEX idx_unique_code (unique_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ");
            
            $extra_json = json_encode($extra_data);
            $stmt = $this->conn->prepare("
                INSERT INTO payment_logs 
                (transaction_id, user_id, unique_code, amount, bank_transaction_ref, status, extra_data) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ");
            $stmt->bind_param("iisdsss", $transaction_id, $user_id, $unique_code, $amount, $bank_ref, $status, $extra_json);
            $stmt->execute();
        } catch (Exception $e) {
            $this->logPayment("Lỗi khi ghi payment log: " . $e->getMessage());
        }
    }
    
    /**
     * Ghi log vào file
     */
    public function logPayment($message) {
        if (!LOG_PAYMENT_ENABLED) return;
        
        try {
            $log_dir = dirname(LOG_FILE_PATH);
            if (!is_dir($log_dir)) {
                mkdir($log_dir, 0755, true);
            }
            
            $timestamp = date('Y-m-d H:i:s');
            $log_message = "[$timestamp] $message" . PHP_EOL;
            file_put_contents(LOG_FILE_PATH, $log_message, FILE_APPEND);
        } catch (Exception $e) {
            error_log("Không thể ghi log: " . $e->getMessage());
        }
    }
    
    /**
     * Gửi email thông báo thanh toán thành công
     */
    private function sendPaymentNotification($user_id, $amount) {
        try {
            // Lấy thông tin user
            $stmt = $this->conn->prepare("SELECT username, email FROM users WHERE id = ?");
            $stmt->bind_param("i", $user_id);
            $stmt->execute();
            $user = $stmt->get_result()->fetch_assoc();
            
            if ($user && !empty($user['email'])) {
                $subject = "Xác nhận nạp tiền thành công";
                $message = "Xin chào {$user['username']},\n\n";
                $message .= "Giao dịch nạp tiền của bạn đã được xác nhận thành công.\n";
                $message .= "Số tiền: " . number_format($amount, 0, ',', '.') . " VND\n";
                $message .= "Thời gian: " . date('d/m/Y H:i:s') . "\n\n";
                $message .= "Cảm ơn bạn đã sử dụng dịch vụ!";
                
                $headers = "From: " . ADMIN_EMAIL;
                mail($user['email'], $subject, $message, $headers);
            }
        } catch (Exception $e) {
            $this->logPayment("Lỗi khi gửi email: " . $e->getMessage());
        }
    }
    
    /**
     * Kiểm tra xem IP có được phép gọi API không
     */
    public function isIpAllowed($ip) {
        global $allowed_webhook_ips;
        return in_array($ip, $allowed_webhook_ips);
    }
    
    /**
     * Xác thực webhook token
     */
    public function validateWebhookToken($token) {
        return hash_equals(WEBHOOK_TOKEN, $token);
    }
}
