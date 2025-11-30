<?php
/**
 * Webhook Payment Handler cho Casso.vn
 * Nhận callback realtime từ Casso khi có giao dịch mới
 * 
 * Cấu hình webhook tại: https://casso.vn
 */

require_once 'db.php';
require_once 'bank_api_casso.php';
require_once 'payment_config.php';

date_default_timezone_set('Asia/Ho_Chi_Minh');

class WebhookCassoHandler {
    private $conn;
    private $cassoAPI;
    private $logFile;

    public function __construct($conn) {
        $this->conn = $conn;
        $this->cassoAPI = new CassoAPI();
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
        $logMessage = "[{$timestamp}] [{$level}] [WebhookCasso] {$message}\n";
        file_put_contents($this->logFile, $logMessage, FILE_APPEND);
    }

    /**
     * Log webhook vào database (optional)
     */
    private function logWebhook($payload, $processed = false) {
        $checkTable = $this->conn->query("SHOW TABLES LIKE 'webhook_logs'");
        if (!$checkTable || $checkTable->num_rows == 0) {
            return;
        }

        $stmt = $this->conn->prepare("
            INSERT INTO webhook_logs (webhook_type, payload, ip_address, processed) 
            VALUES ('casso', ?, ?, ?)
        ");
        
        $ipAddress = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? '';
        $stmt->bind_param("ssi", $payload, $ipAddress, $processed);
        $stmt->execute();
    }

    /**
     * Xử lý webhook từ Casso
     */
    public function handleWebhook() {
        // Lấy raw payload
        $payload = file_get_contents('php://input');
        $this->log("Nhận webhook từ Casso: " . substr($payload, 0, 200));

        if (!WEBHOOK_ENABLED) {
            $this->log("Webhook bị tắt trong config", 'WARNING');
            $this->sendResponse(403, ['error' => 'Webhook disabled']);
            return;
        }

        // Log webhook
        $this->logWebhook($payload, false);

        // Parse JSON
        $data = json_decode($payload, true);
        if (!$data) {
            $this->log("Không thể parse JSON", 'ERROR');
            $this->sendResponse(400, ['error' => 'Invalid JSON']);
            return;
        }

        // Verify IP (Casso không dùng signature mà dùng IP whitelist)
        if (!$this->cassoAPI->verifyWebhookSignature($payload, '')) {
            $this->log("IP không được whitelist", 'WARNING');
            // Vẫn xử lý nhưng log warning
        }

        // Xử lý từng transaction trong webhook
        $transactions = $data['data'] ?? [$data];
        $processedCount = 0;

        foreach ($transactions as $transaction) {
            if ($this->processTransaction($transaction)) {
                $processedCount++;
            }
        }

        // Update webhook log
        $this->logWebhook($payload, true);

        $this->log("Đã xử lý {$processedCount} giao dịch từ webhook");
        $this->sendResponse(200, ['success' => true, 'processed' => $processedCount]);
    }

    /**
     * Xử lý một transaction từ webhook
     */
    private function processTransaction($transaction) {
        $normalized = $this->cassoAPI->normalizeTransaction($transaction);
        
        // Chỉ xử lý giao dịch IN (tiền vào)
        if ($normalized['type'] !== 'IN') {
            $this->log("Bỏ qua giao dịch OUT: " . $normalized['transaction_id']);
            return false;
        }

        $amount = $normalized['amount'];
        $description = $normalized['description'];
        $bankTransactionId = $normalized['transaction_id'];

        $this->log("Xử lý giao dịch: {$bankTransactionId} - Amount: {$amount} - Desc: {$description}");

        // Parse mã giao dịch từ description
        $transactionCode = $this->cassoAPI->parseTransactionCode($description);
        
        if (!$transactionCode) {
            $this->log("Không tìm thấy mã giao dịch trong description", 'WARNING');
            return false;
        }

        // Tìm giao dịch pending trong database
        $stmt = $this->conn->prepare("
            SELECT transaction_id, user_id, amount_paid, status 
            FROM transactions 
            WHERE unique_code = ? AND status = 'pending'
        ");
        $stmt->bind_param("s", $transactionCode);
        $stmt->execute();
        $pending = $stmt->get_result()->fetch_assoc();

        if (!$pending) {
            $this->log("Không tìm thấy giao dịch pending với mã: {$transactionCode}", 'WARNING');
            return false;
        }

        // Kiểm tra số tiền khớp
        if (abs($amount - $pending['amount_paid']) >= 1) {
            $this->log("Số tiền không khớp: Expected {$pending['amount_paid']}, Got {$amount}", 'WARNING');
            return false;
        }

        // Cập nhật trạng thái thành công
        try {
            $this->conn->begin_transaction();

            // Update transaction
            $stmt = $this->conn->prepare("
                UPDATE transactions 
                SET status = 'success', updated_at = NOW() 
                WHERE transaction_id = ?
            ");
            $stmt->bind_param("i", $pending['transaction_id']);
            $stmt->execute();

            // Update user balance
            $stmt2 = $this->conn->prepare("
                UPDATE users 
                SET balance = balance + ? 
                WHERE id = ?
            ");
            $stmt2->bind_param("di", $pending['amount_paid'], $pending['user_id']);
            $stmt2->execute();

            // Cache bank transaction (optional)
            $this->cacheBankTransaction($normalized, $pending['transaction_id']);

            $this->conn->commit();

            $this->log("✅ Xử lý thành công webhook: {$transactionCode} - User {$pending['user_id']} - Amount {$amount}", 'SUCCESS');
            return true;

        } catch (Exception $e) {
            $this->conn->rollback();
            $this->log("Lỗi xử lý webhook: " . $e->getMessage(), 'ERROR');
            return false;
        }
    }

    /**
     * Lưu giao dịch ngân hàng vào cache
     */
    private function cacheBankTransaction($normalized, $matchedTransactionId) {
        $checkTable = $this->conn->query("SHOW TABLES LIKE 'bank_transactions'");
        if (!$checkTable || $checkTable->num_rows == 0) {
            return;
        }

        $stmt = $this->conn->prepare("
            INSERT INTO bank_transactions (
                bank_transaction_id, amount, description, transaction_date, 
                transaction_type, balance_after, matched, matched_transaction_id, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON DUPLICATE KEY UPDATE
                matched = 1,
                matched_transaction_id = VALUES(matched_transaction_id)
        ");

        $rawData = json_encode($normalized);
        $stmt->bind_param(
            "sdsssdis",
            $normalized['transaction_id'],
            $normalized['amount'],
            $normalized['description'],
            $normalized['transaction_date'],
            $normalized['type'],
            $normalized['balance'],
            $matchedTransactionId,
            $rawData
        );

        $stmt->execute();
    }

    /**
     * Gửi response
     */
    private function sendResponse($statusCode, $data) {
        http_response_code($statusCode);
        header('Content-Type: application/json');
        echo json_encode($data);
        exit;
    }
}

// Xử lý webhook request
$handler = new WebhookCassoHandler($conn);
$handler->handleWebhook();

?>
