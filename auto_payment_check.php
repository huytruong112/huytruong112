<?php
/**
 * Auto Payment Check - Kiểm tra và xử lý giao dịch tự động
 * Script này sẽ:
 * 1. Lấy danh sách giao dịch pending từ DB
 * 2. Lấy danh sách giao dịch từ ngân hàng
 * 3. So khớp và cập nhật trạng thái + số dư
 */

require_once 'db.php';
require_once 'bank_api_helper.php';
require_once 'payment_config.php';

class AutoPaymentProcessor {
    private $conn;
    private $bankAPI;
    private $logFile;

    public function __construct($conn) {
        $this->conn = $conn;
        $this->bankAPI = new BankAPIHelper();
        $this->logFile = PAYMENT_LOG_PATH;
        $this->ensureLogDirectory();
    }

    private function ensureLogDirectory() {
        $logDir = dirname($this->logFile);
        if (!file_exists($logDir)) {
            mkdir($logDir, 0755, true);
        }
    }

    private function log($message, $level = 'INFO') {
        if (!PAYMENT_LOG_ENABLED) return;
        $timestamp = date('Y-m-d H:i:s');
        $logMessage = "[{$timestamp}] [{$level}] [AutoPayment] {$message}\n";
        file_put_contents($this->logFile, $logMessage, FILE_APPEND);
    }

    /**
     * Lấy danh sách giao dịch pending từ database
     */
    private function getPendingTransactions() {
        $sql = "SELECT transaction_id, user_id, amount_paid, unique_code, transaction_date 
                FROM transactions 
                WHERE status = 'pending' 
                AND transaction_date > DATE_SUB(NOW(), INTERVAL 24 HOUR)
                ORDER BY transaction_date DESC";
        
        $result = $this->conn->query($sql);
        $transactions = [];
        
        if ($result && $result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                $transactions[] = $row;
            }
        }
        
        return $transactions;
    }

    /**
     * Cập nhật trạng thái giao dịch thành công
     */
    private function updateTransactionSuccess($transactionId, $userId, $amount) {
        try {
            // Bắt đầu transaction
            $this->conn->begin_transaction();

            // 1. Cập nhật trạng thái giao dịch
            $stmt = $this->conn->prepare("UPDATE transactions SET status = 'success', updated_at = NOW() WHERE transaction_id = ?");
            $stmt->bind_param("i", $transactionId);
            $stmt->execute();

            // 2. Cập nhật số dư user
            $stmt2 = $this->conn->prepare("UPDATE users SET balance = balance + ? WHERE id = ?");
            $stmt2->bind_param("di", $amount, $userId);
            $stmt2->execute();

            // Commit transaction
            $this->conn->commit();

            $this->log("Cập nhật thành công transaction ID {$transactionId} - User ID {$userId} - Amount {$amount}", 'SUCCESS');
            return true;

        } catch (Exception $e) {
            $this->conn->rollback();
            $this->log("Lỗi cập nhật transaction ID {$transactionId}: " . $e->getMessage(), 'ERROR');
            return false;
        }
    }

    /**
     * Hủy giao dịch quá hạn (> 24h)
     */
    private function cancelExpiredTransactions() {
        if (!AUTO_CANCEL_ENABLED) return;

        $sql = "UPDATE transactions 
                SET status = 'cancelled' 
                WHERE status = 'pending' 
                AND transaction_date < DATE_SUB(NOW(), INTERVAL 24 HOUR)";
        
        $result = $this->conn->query($sql);
        
        if ($result && $this->conn->affected_rows > 0) {
            $this->log("Đã hủy {$this->conn->affected_rows} giao dịch quá hạn", 'INFO');
        }
    }

    /**
     * Kiểm tra và xử lý giao dịch tự động
     */
    public function process() {
        $this->log("===== Bắt đầu kiểm tra thanh toán tự động =====");

        if (!PAYMENT_AUTO_CHECK_ENABLED) {
            $this->log("Auto check bị tắt trong config", 'WARNING');
            return;
        }

        // 1. Hủy giao dịch quá hạn
        $this->cancelExpiredTransactions();

        // 2. Lấy danh sách giao dịch pending
        $pendingTransactions = $this->getPendingTransactions();
        
        if (empty($pendingTransactions)) {
            $this->log("Không có giao dịch pending nào", 'INFO');
            return;
        }

        $this->log("Tìm thấy " . count($pendingTransactions) . " giao dịch pending");

        // 3. Lấy danh sách giao dịch từ ngân hàng (24h gần nhất)
        $fromDate = date('d/m/Y', strtotime('-1 day'));
        $toDate = date('d/m/Y');
        
        $bankTransactions = $this->bankAPI->getTransactions($fromDate, $toDate);
        
        if (empty($bankTransactions)) {
            $this->log("Không lấy được giao dịch từ ngân hàng hoặc không có giao dịch mới", 'WARNING');
            return;
        }

        $this->log("Lấy được " . count($bankTransactions) . " giao dịch từ ngân hàng");

        // 4. So khớp giao dịch
        $matchCount = 0;
        foreach ($pendingTransactions as $pending) {
            foreach ($bankTransactions as $bankTx) {
                $normalized = $this->bankAPI->normalizeTransaction($bankTx);
                
                // Parse mã giao dịch từ description
                $transactionCode = $this->bankAPI->parseTransactionCode($normalized['description']);
                
                if (!$transactionCode) continue;

                // Kiểm tra khớp mã và số tiền
                if ($transactionCode === $pending['unique_code'] && 
                    abs($normalized['amount'] - $pending['amount_paid']) < 1) {
                    
                    $this->log("Tìm thấy giao dịch khớp: {$transactionCode} - Số tiền: {$normalized['amount']}", 'SUCCESS');
                    
                    // Cập nhật trạng thái
                    if ($this->updateTransactionSuccess(
                        $pending['transaction_id'],
                        $pending['user_id'],
                        $pending['amount_paid']
                    )) {
                        $matchCount++;
                        
                        // Gửi thông báo cho user (optional)
                        $this->sendNotificationToUser($pending['user_id'], $pending['amount_paid']);
                    }
                    
                    break; // Tìm được rồi thì break
                }
            }
        }

        $this->log("===== Hoàn thành: Đã xử lý {$matchCount} giao dịch =====");
    }

    /**
     * Gửi thông báo cho user (có thể dùng email, SMS, etc.)
     */
    private function sendNotificationToUser($userId, $amount) {
        // TODO: Implement notification logic
        // Có thể gửi email, push notification, SMS, etc.
        $this->log("Gửi thông báo cho user {$userId} về số tiền {$amount}", 'INFO');
    }

    /**
     * Kiểm tra một giao dịch cụ thể theo mã
     */
    public function checkSingleTransaction($uniqueCode) {
        $this->log("Kiểm tra giao dịch đơn lẻ: {$uniqueCode}");

        // Lấy thông tin transaction từ DB
        $stmt = $this->conn->prepare("SELECT transaction_id, user_id, amount_paid, unique_code, status 
                                       FROM transactions 
                                       WHERE unique_code = ? AND status = 'pending'");
        $stmt->bind_param("s", $uniqueCode);
        $stmt->execute();
        $pending = $stmt->get_result()->fetch_assoc();

        if (!$pending) {
            $this->log("Không tìm thấy giao dịch pending với mã {$uniqueCode}", 'WARNING');
            return ['success' => false, 'message' => 'Giao dịch không tồn tại hoặc đã xử lý'];
        }

        // Lấy giao dịch từ ngân hàng
        $bankTransactions = $this->bankAPI->getTransactions(
            date('d/m/Y', strtotime('-1 day')),
            date('d/m/Y')
        );

        foreach ($bankTransactions as $bankTx) {
            $normalized = $this->bankAPI->normalizeTransaction($bankTx);
            $transactionCode = $this->bankAPI->parseTransactionCode($normalized['description']);

            if ($transactionCode === $uniqueCode && 
                abs($normalized['amount'] - $pending['amount_paid']) < 1) {
                
                // Tìm thấy giao dịch khớp
                if ($this->updateTransactionSuccess(
                    $pending['transaction_id'],
                    $pending['user_id'],
                    $pending['amount_paid']
                )) {
                    return [
                        'success' => true,
                        'message' => 'Giao dịch đã được xác nhận thành công',
                        'status' => 'success'
                    ];
                }
            }
        }

        return [
            'success' => false,
            'message' => 'Chưa tìm thấy giao dịch khớp từ ngân hàng',
            'status' => 'pending'
        ];
    }
}

// Nếu chạy trực tiếp file này
if (php_sapi_name() === 'cli' || !isset($_SERVER['REQUEST_METHOD'])) {
    $processor = new AutoPaymentProcessor($conn);
    $processor->process();
}

?>
