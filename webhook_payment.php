<?php
/**
 * Webhook Payment Handler
 * Nhận callback từ ngân hàng hoặc payment gateway khi có giao dịch mới
 */

require_once 'db.php';
require_once 'auto_payment_check.php';
require_once 'payment_config.php';

// Thiết lập múi giờ
date_default_timezone_set('Asia/Ho_Chi_Minh');

class WebhookPaymentHandler {
    private $conn;
    private $logFile;

    public function __construct($conn) {
        $this->conn = $conn;
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
        $logMessage = "[{$timestamp}] [{$level}] [Webhook] {$message}\n";
        file_put_contents($this->logFile, $logMessage, FILE_APPEND);
    }

    /**
     * Xác thực webhook signature
     */
    private function verifySignature($payload, $signature) {
        $expectedSignature = hash_hmac('sha256', $payload, WEBHOOK_SECRET);
        return hash_equals($expectedSignature, $signature);
    }

    /**
     * Xử lý webhook từ ngân hàng
     */
    public function handleWebhook() {
        // Lấy raw payload
        $payload = file_get_contents('php://input');
        $this->log("Nhận webhook: " . substr($payload, 0, 200));

        if (!WEBHOOK_ENABLED) {
            $this->log("Webhook bị tắt trong config", 'WARNING');
            $this->sendResponse(403, ['error' => 'Webhook disabled']);
            return;
        }

        // Verify signature
        $signature = $_SERVER['HTTP_X_WEBHOOK_SIGNATURE'] ?? '';
        if (!$this->verifySignature($payload, $signature)) {
            $this->log("Signature không hợp lệ", 'ERROR');
            $this->sendResponse(401, ['error' => 'Invalid signature']);
            return;
        }

        // Parse JSON
        $data = json_decode($payload, true);
        if (!$data) {
            $this->log("Không thể parse JSON", 'ERROR');
            $this->sendResponse(400, ['error' => 'Invalid JSON']);
            return;
        }

        // Xử lý theo loại webhook
        $type = $data['type'] ?? '';
        
        switch ($type) {
            case 'transaction.created':
                $this->handleTransactionCreated($data);
                break;
            case 'transaction.updated':
                $this->handleTransactionUpdated($data);
                break;
            default:
                $this->log("Loại webhook không được hỗ trợ: {$type}", 'WARNING');
                $this->sendResponse(400, ['error' => 'Unsupported webhook type']);
                return;
        }

        $this->sendResponse(200, ['success' => true]);
    }

    /**
     * Xử lý webhook khi có giao dịch mới
     */
    private function handleTransactionCreated($data) {
        $this->log("Xử lý transaction.created");

        $transaction = $data['data'] ?? [];
        
        $amount = floatval($transaction['amount'] ?? 0);
        $description = $transaction['description'] ?? '';
        $bankTransactionId = $transaction['transaction_id'] ?? '';

        // Parse mã giao dịch từ description
        if (preg_match('/TS\d{5}/', $description, $matches)) {
            $uniqueCode = $matches[0];
            
            // Kiểm tra giao dịch pending trong DB
            $stmt = $this->conn->prepare("SELECT transaction_id, user_id, amount_paid, status 
                                           FROM transactions 
                                           WHERE unique_code = ? AND status = 'pending'");
            $stmt->bind_param("s", $uniqueCode);
            $stmt->execute();
            $pending = $stmt->get_result()->fetch_assoc();

            if ($pending && abs($amount - $pending['amount_paid']) < 1) {
                // Khớp - cập nhật trạng thái
                $processor = new AutoPaymentProcessor($this->conn);
                $processor->checkSingleTransaction($uniqueCode);
                
                $this->log("Đã xử lý giao dịch webhook: {$uniqueCode}", 'SUCCESS');
            } else {
                $this->log("Không tìm thấy giao dịch khớp cho mã: {$uniqueCode}", 'WARNING');
            }
        }
    }

    /**
     * Xử lý webhook khi giao dịch được cập nhật
     */
    private function handleTransactionUpdated($data) {
        $this->log("Xử lý transaction.updated");
        // Tương tự handleTransactionCreated
        $this->handleTransactionCreated($data);
    }

    /**
     * Gửi response về webhook
     */
    private function sendResponse($statusCode, $data) {
        http_response_code($statusCode);
        header('Content-Type: application/json');
        echo json_encode($data);
        exit;
    }
}

// Xử lý webhook request
$handler = new WebhookPaymentHandler($conn);
$handler->handleWebhook();

?>
