<?php
/**
 * Class xử lý thanh toán tự động
 * 
 * Xử lý logic:
 * - Nhận dữ liệu từ webhook
 * - Validate giao dịch
 * - Cập nhật số dư user
 * - Log giao dịch
 */

require_once 'payment_config.php';

class PaymentProcessor {
    private $conn;
    
    public function __construct($dbConnection) {
        $this->conn = $dbConnection;
    }
    
    /**
     * Xử lý giao dịch từ Casso.vn
     * 
     * @param array $data Dữ liệu từ webhook Casso
     * @return array Kết quả xử lý
     */
    public function processCassoWebhook($data) {
        paymentLog("Bắt đầu xử lý Casso webhook: " . json_encode($data, JSON_UNESCAPED_UNICODE));
        
        // Validate dữ liệu từ Casso
        if (!isset($data['data']) || !is_array($data['data'])) {
            paymentLog("Dữ liệu Casso không hợp lệ", "ERROR");
            return ['success' => false, 'message' => 'Invalid data format'];
        }
        
        $results = [];
        foreach ($data['data'] as $transaction) {
            $result = $this->processTransaction([
                'amount' => $transaction['amount'] ?? 0,
                'description' => $transaction['description'] ?? '',
                'transaction_date' => $transaction['when'] ?? date('Y-m-d H:i:s'),
                'reference_number' => $transaction['tid'] ?? '',
                'bank_account' => $transaction['bank_sub_acc_id'] ?? '',
                'source' => 'casso'
            ]);
            $results[] = $result;
        }
        
        return [
            'success' => true,
            'processed' => count($results),
            'results' => $results
        ];
    }
    
    /**
     * Xử lý giao dịch từ Payos.vn
     */
    public function processPayosWebhook($data) {
        paymentLog("Bắt đầu xử lý Payos webhook: " . json_encode($data, JSON_UNESCAPED_UNICODE));
        
        return $this->processTransaction([
            'amount' => $data['amount'] ?? 0,
            'description' => $data['description'] ?? '',
            'transaction_date' => $data['transactionDateTime'] ?? date('Y-m-d H:i:s'),
            'reference_number' => $data['reference'] ?? '',
            'source' => 'payos'
        ]);
    }
    
    /**
     * Xử lý giao dịch chung
     * 
     * @param array $txData {
     *   amount: số tiền
     *   description: nội dung chuyển khoản
     *   transaction_date: thời gian giao dịch
     *   reference_number: mã tham chiếu từ ngân hàng
     *   source: nguồn (casso/payos/bank)
     * }
     * @return array
     */
    public function processTransaction($txData) {
        $amount = floatval($txData['amount'] ?? 0);
        $description = trim($txData['description'] ?? '');
        $txDate = $txData['transaction_date'] ?? date('Y-m-d H:i:s');
        $refNumber = $txData['reference_number'] ?? '';
        $source = $txData['source'] ?? 'unknown';
        
        paymentLog("Xử lý giao dịch: amount={$amount}, description={$description}, ref={$refNumber}");
        
        // Kiểm tra số tiền hợp lệ
        if ($amount < MIN_TRANSACTION_AMOUNT) {
            paymentLog("Số tiền quá nhỏ: {$amount}", "WARNING");
            return ['success' => false, 'message' => 'Amount too small', 'amount' => $amount];
        }
        
        if ($amount > MAX_TRANSACTION_AMOUNT) {
            paymentLog("Số tiền quá lớn: {$amount}", "WARNING");
            return ['success' => false, 'message' => 'Amount too large', 'amount' => $amount];
        }
        
        // Tìm mã giao dịch trong nội dung chuyển khoản
        $uniqueCode = $this->extractUniqueCode($description);
        if (!$uniqueCode) {
            paymentLog("Không tìm thấy mã giao dịch trong: {$description}", "WARNING");
            return ['success' => false, 'message' => 'No transaction code found', 'description' => $description];
        }
        
        paymentLog("Tìm thấy mã giao dịch: {$uniqueCode}");
        
        // Tìm giao dịch trong database
        $stmt = $this->conn->prepare("
            SELECT transaction_id, user_id, amount_paid, status, transaction_date 
            FROM transactions 
            WHERE unique_code = ? 
            LIMIT 1
        ");
        $stmt->bind_param("s", $uniqueCode);
        $stmt->execute();
        $transaction = $stmt->get_result()->fetch_assoc();
        
        if (!$transaction) {
            paymentLog("Không tìm thấy giao dịch với mã: {$uniqueCode}", "WARNING");
            return ['success' => false, 'message' => 'Transaction not found', 'code' => $uniqueCode];
        }
        
        $transactionId = $transaction['transaction_id'];
        $userId = $transaction['user_id'];
        $expectedAmount = floatval($transaction['amount_paid']);
        $currentStatus = $transaction['status'];
        
        paymentLog("Tìm thấy giao dịch ID={$transactionId}, User ID={$userId}, Amount={$expectedAmount}, Status={$currentStatus}");
        
        // Kiểm tra trạng thái
        if ($currentStatus === 'success' || $currentStatus === 'Thành công') {
            paymentLog("Giao dịch đã được xử lý trước đó", "WARNING");
            return ['success' => false, 'message' => 'Already processed', 'transaction_id' => $transactionId];
        }
        
        // Kiểm tra timeout
        $txTimestamp = strtotime($transaction['transaction_date']);
        if (time() - $txTimestamp > TRANSACTION_TIMEOUT) {
            paymentLog("Giao dịch đã quá hạn", "WARNING");
            $this->markTransactionCancelled($transactionId);
            return ['success' => false, 'message' => 'Transaction expired', 'transaction_id' => $transactionId];
        }
        
        // Kiểm tra số tiền khớp (cho phép sai số nhỏ hoặc nhiều hơn)
        if ($amount < $expectedAmount * 0.99) { // Cho phép thiếu 1%
            paymentLog("Số tiền không khớp: Nhận {$amount}, Mong đợi {$expectedAmount}", "WARNING");
            return ['success' => false, 'message' => 'Amount mismatch', 'received' => $amount, 'expected' => $expectedAmount];
        }
        
        // Bắt đầu transaction
        $this->conn->begin_transaction();
        
        try {
            // Cập nhật trạng thái giao dịch
            $stmt = $this->conn->prepare("
                UPDATE transactions 
                SET status = 'success', 
                    updated_at = NOW()
                WHERE transaction_id = ?
            ");
            $stmt->bind_param("i", $transactionId);
            $stmt->execute();
            
            // Cộng tiền vào tài khoản user
            $stmt = $this->conn->prepare("
                UPDATE users 
                SET balance = balance + ? 
                WHERE id = ?
            ");
            $stmt->bind_param("di", $expectedAmount, $userId);
            $stmt->execute();
            
            // Lưu log vào payment_logs
            $this->savePaymentLog([
                'transaction_id' => $transactionId,
                'user_id' => $userId,
                'amount' => $amount,
                'expected_amount' => $expectedAmount,
                'unique_code' => $uniqueCode,
                'description' => $description,
                'reference_number' => $refNumber,
                'source' => $source,
                'status' => 'success',
                'raw_data' => json_encode($txData, JSON_UNESCAPED_UNICODE)
            ]);
            
            $this->conn->commit();
            
            paymentLog("✓ Xử lý thành công giao dịch ID={$transactionId}, User ID={$userId}, Amount={$expectedAmount}", "SUCCESS");
            
            // Gửi thông báo
            if (NOTIFY_USER_ON_SUCCESS) {
                $this->notifyUser($userId, $expectedAmount, $uniqueCode);
            }
            
            return [
                'success' => true,
                'message' => 'Payment processed successfully',
                'transaction_id' => $transactionId,
                'user_id' => $userId,
                'amount' => $expectedAmount
            ];
            
        } catch (Exception $e) {
            $this->conn->rollback();
            paymentLog("✗ Lỗi xử lý giao dịch: " . $e->getMessage(), "ERROR");
            
            return [
                'success' => false,
                'message' => 'Database error: ' . $e->getMessage(),
                'transaction_id' => $transactionId
            ];
        }
    }
    
    /**
     * Trích xuất mã giao dịch từ nội dung chuyển khoản
     * Format: TS12345 hoặc ts12345
     */
    private function extractUniqueCode($description) {
        $description = strtoupper(trim($description));
        
        // Pattern 1: TS + 5 chữ số
        if (preg_match('/TS\d{5}/', $description, $matches)) {
            return $matches[0];
        }
        
        // Pattern 2: Tìm bất kỳ mã nào có format tương tự
        if (preg_match('/[A-Z]{2}\d{5}/', $description, $matches)) {
            return $matches[0];
        }
        
        return null;
    }
    
    /**
     * Lưu log thanh toán vào database
     */
    private function savePaymentLog($logData) {
        $stmt = $this->conn->prepare("
            INSERT INTO payment_logs 
            (transaction_id, user_id, amount, expected_amount, unique_code, description, reference_number, source, status, raw_data, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
        ");
        
        $stmt->bind_param(
            "iiddsssss",
            $logData['transaction_id'],
            $logData['user_id'],
            $logData['amount'],
            $logData['expected_amount'],
            $logData['unique_code'],
            $logData['description'],
            $logData['reference_number'],
            $logData['source'],
            $logData['status'],
            $logData['raw_data']
        );
        
        $stmt->execute();
    }
    
    /**
     * Đánh dấu giao dịch bị hủy
     */
    private function markTransactionCancelled($transactionId) {
        $stmt = $this->conn->prepare("
            UPDATE transactions 
            SET status = 'cancelled' 
            WHERE transaction_id = ?
        ");
        $stmt->bind_param("i", $transactionId);
        $stmt->execute();
    }
    
    /**
     * Gửi thông báo cho user
     */
    private function notifyUser($userId, $amount, $code) {
        // TODO: Implement notification (Email, SMS, Telegram, etc.)
        paymentLog("Gửi thông báo cho User ID={$userId}, Amount={$amount}, Code={$code}");
        
        // Ví dụ: Lưu vào bảng notifications
        // $stmt = $this->conn->prepare("INSERT INTO notifications (user_id, title, message, created_at) VALUES (?, ?, ?, NOW())");
        // ...
    }
    
    /**
     * Kiểm tra giao dịch trùng lặp (để tránh xử lý 2 lần)
     */
    public function isDuplicateWebhook($refNumber, $amount, $description) {
        if (!$refNumber) return false;
        
        $stmt = $this->conn->prepare("
            SELECT id FROM payment_logs 
            WHERE reference_number = ? 
            AND amount = ? 
            AND description = ? 
            AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            LIMIT 1
        ");
        $stmt->bind_param("sds", $refNumber, $amount, $description);
        $stmt->execute();
        $result = $stmt->get_result();
        
        return $result->num_rows > 0;
    }
}
