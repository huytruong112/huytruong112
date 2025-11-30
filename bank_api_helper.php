<?php
/**
 * Bank API Helper - Kết nối với API ngân hàng
 * Hỗ trợ nhiều ngân hàng tại Việt Nam
 */

require_once 'payment_config.php';

class BankAPIHelper {
    private $bankType;
    private $sessionToken = null;
    private $logFile;

    public function __construct($bankType = BANK_API_TYPE) {
        $this->bankType = $bankType;
        $this->logFile = PAYMENT_LOG_PATH;
        $this->ensureLogDirectory();
    }

    /**
     * Đảm bảo thư mục log tồn tại
     */
    private function ensureLogDirectory() {
        $logDir = dirname($this->logFile);
        if (!file_exists($logDir)) {
            mkdir($logDir, 0755, true);
        }
    }

    /**
     * Ghi log
     */
    private function log($message, $level = 'INFO') {
        if (!PAYMENT_LOG_ENABLED) return;
        $timestamp = date('Y-m-d H:i:s');
        $logMessage = "[{$timestamp}] [{$level}] {$message}\n";
        file_put_contents($this->logFile, $logMessage, FILE_APPEND);
    }

    /**
     * Đăng nhập vào ngân hàng và lấy token
     */
    public function login() {
        $this->log("Đang đăng nhập vào {$this->bankType}...");
        
        switch ($this->bankType) {
            case 'vcb':
                return $this->loginVCB();
            case 'mbbank':
                return $this->loginMBBank();
            case 'acb':
                return $this->loginACB();
            case 'tpbank':
                return $this->loginTPBank();
            case 'techcombank':
                return $this->loginTechcombank();
            case 'vietinbank':
                return $this->loginVietinBank();
            default:
                $this->log("Loại ngân hàng không được hỗ trợ: {$this->bankType}", 'ERROR');
                return false;
        }
    }

    /**
     * Lấy danh sách giao dịch
     */
    public function getTransactions($fromDate = null, $toDate = null) {
        if (!$this->sessionToken && !$this->login()) {
            $this->log("Không thể đăng nhập để lấy giao dịch", 'ERROR');
            return [];
        }

        $this->log("Đang lấy danh sách giao dịch từ {$this->bankType}...");

        switch ($this->bankType) {
            case 'vcb':
                return $this->getTransactionsVCB($fromDate, $toDate);
            case 'mbbank':
                return $this->getTransactionsMBBank($fromDate, $toDate);
            case 'acb':
                return $this->getTransactionsACB($fromDate, $toDate);
            case 'tpbank':
                return $this->getTransactionsTPBank($fromDate, $toDate);
            case 'techcombank':
                return $this->getTransactionsTechcombank($fromDate, $toDate);
            case 'vietinbank':
                return $this->getTransactionsVietinBank($fromDate, $toDate);
            default:
                return [];
        }
    }

    // ===== VCB (VIETCOMBANK) =====
    private function loginVCB() {
        // Implement VCB login logic
        // API này thường cần reverse engineering từ app
        $this->log("VCB login - chưa implement đầy đủ (cần cấu hình thực tế)", 'WARNING');
        return true; // Tạm thời return true để test
    }

    private function getTransactionsVCB($fromDate, $toDate) {
        // Implement VCB transaction history
        $this->log("VCB getTransactions - chưa implement đầy đủ", 'WARNING');
        return [];
    }

    // ===== MB BANK =====
    private function loginMBBank() {
        if (empty(MB_USERNAME) || empty(MB_PASSWORD)) {
            $this->log("Chưa cấu hình MB Bank credentials", 'ERROR');
            return false;
        }

        try {
            $ch = curl_init(MB_API_URL . '/api/retail-web-internetbankingms/getCaptchaImage');
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
            curl_setopt($ch, CURLOPT_HTTPHEADER, [
                'Content-Type: application/json',
                'User-Agent: Mozilla/5.0',
                'X-Request-Id: ' . $this->generateRequestId()
            ]);
            
            $captchaResponse = curl_exec($ch);
            curl_close($ch);

            // Login với captcha (cần xử lý captcha - có thể dùng AI/OCR)
            $this->log("MB Bank login - cần xử lý captcha", 'WARNING');
            return true;
        } catch (Exception $e) {
            $this->log("MB Bank login error: " . $e->getMessage(), 'ERROR');
            return false;
        }
    }

    private function getTransactionsMBBank($fromDate, $toDate) {
        if (empty($fromDate)) $fromDate = date('d/m/Y', strtotime('-7 days'));
        if (empty($toDate)) $toDate = date('d/m/Y');

        $this->log("MB Bank getTransactions - chưa implement đầy đủ", 'WARNING');
        return [];
    }

    // ===== ACB =====
    private function loginACB() {
        $this->log("ACB login - chưa implement đầy đủ", 'WARNING');
        return true;
    }

    private function getTransactionsACB($fromDate, $toDate) {
        $this->log("ACB getTransactions - chưa implement đầy đủ", 'WARNING');
        return [];
    }

    // ===== TP BANK =====
    private function loginTPBank() {
        $this->log("TPBank login - chưa implement đầy đủ", 'WARNING');
        return true;
    }

    private function getTransactionsTPBank($fromDate, $toDate) {
        $this->log("TPBank getTransactions - chưa implement đầy đủ", 'WARNING');
        return [];
    }

    // ===== TECHCOMBANK =====
    private function loginTechcombank() {
        $this->log("Techcombank login - chưa implement đầy đủ", 'WARNING');
        return true;
    }

    private function getTransactionsTechcombank($fromDate, $toDate) {
        $this->log("Techcombank getTransactions - chưa implement đầy đủ", 'WARNING');
        return [];
    }

    // ===== VIETINBANK =====
    private function loginVietinBank() {
        $this->log("VietinBank login - chưa implement đầy đủ", 'WARNING');
        return true;
    }

    private function getTransactionsVietinBank($fromDate, $toDate) {
        $this->log("VietinBank getTransactions - chưa implement đầy đủ", 'WARNING');
        return [];
    }

    // ===== HELPER METHODS =====
    private function generateRequestId() {
        return time() . rand(1000, 9999);
    }

    /**
     * Chuẩn hóa format giao dịch từ các ngân hàng khác nhau
     */
    public function normalizeTransaction($transaction) {
        return [
            'transaction_id' => $transaction['id'] ?? '',
            'amount' => floatval($transaction['amount'] ?? 0),
            'description' => $transaction['description'] ?? '',
            'transaction_date' => $transaction['date'] ?? date('Y-m-d H:i:s'),
            'type' => $transaction['type'] ?? 'IN', // IN hoặc OUT
            'balance' => floatval($transaction['balance'] ?? 0)
        ];
    }

    /**
     * Parse mã giao dịch từ description
     * Ví dụ: "TS12345 Nap tien" -> TS12345
     */
    public function parseTransactionCode($description) {
        // Tìm pattern TSxxxxx trong description
        if (preg_match('/TS\d{5}/', $description, $matches)) {
            return $matches[0];
        }
        return null;
    }
}

?>
