<?php
/**
 * Casso.vn API Integration
 * Service tự động check giao dịch ngân hàng (Khuyến nghị sử dụng)
 * 
 * Đăng ký tài khoản tại: https://casso.vn
 * Lấy API Key tại: https://casso.vn/user/setting/keys
 */

require_once 'payment_config.php';

class CassoAPI {
    private $apiKey;
    private $apiUrl = 'https://oauth.casso.vn/v2';
    private $logFile;

    public function __construct($apiKey = null) {
        $this->apiKey = $apiKey ?? COMMUNITY_API_KEY;
        $this->logFile = PAYMENT_LOG_PATH;
    }

    private function log($message, $level = 'INFO') {
        if (!PAYMENT_LOG_ENABLED) return;
        $timestamp = date('Y-m-d H:i:s');
        $logMessage = "[{$timestamp}] [{$level}] [Casso] {$message}\n";
        file_put_contents($this->logFile, $logMessage, FILE_APPEND);
    }

    /**
     * Lấy danh sách giao dịch
     * 
     * @param int $fromDate Timestamp bắt đầu (tính bằng milliseconds)
     * @param int $toDate Timestamp kết thúc (tính bằng milliseconds)
     * @param int $page Page number (mặc định 1)
     * @param int $pageSize Số record mỗi page (max 100)
     * @return array
     */
    public function getTransactions($fromDate = null, $toDate = null, $page = 1, $pageSize = 20) {
        if (empty($this->apiKey)) {
            $this->log("API Key chưa được cấu hình", 'ERROR');
            return [];
        }

        // Default: lấy giao dịch 24h gần nhất
        if ($fromDate === null) {
            $fromDate = strtotime('-24 hours') * 1000;
        }
        if ($toDate === null) {
            $toDate = time() * 1000;
        }

        $url = $this->apiUrl . '/transactions';
        $params = [
            'fromDate' => $fromDate,
            'toDate' => $toDate,
            'page' => $page,
            'pageSize' => min($pageSize, 100) // Max 100
        ];

        $url .= '?' . http_build_query($params);

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_HTTPHEADER => [
                'Authorization: Apikey ' . $this->apiKey,
                'Content-Type: application/json'
            ],
            CURLOPT_TIMEOUT => 30
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            $this->log("API request failed with HTTP code {$httpCode}", 'ERROR');
            return [];
        }

        $data = json_decode($response, true);
        
        if (!$data || !isset($data['data'])) {
            $this->log("Invalid API response", 'ERROR');
            return [];
        }

        $this->log("Lấy được " . count($data['data']['records']) . " giao dịch từ Casso");
        
        return $data['data']['records'] ?? [];
    }

    /**
     * Lấy thông tin tài khoản ngân hàng đã liên kết
     */
    public function getBankAccounts() {
        if (empty($this->apiKey)) {
            $this->log("API Key chưa được cấu hình", 'ERROR');
            return [];
        }

        $url = $this->apiUrl . '/userInfo';

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_HTTPHEADER => [
                'Authorization: Apikey ' . $this->apiKey,
                'Content-Type: application/json'
            ],
            CURLOPT_TIMEOUT => 30
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            $this->log("Get bank accounts failed with HTTP code {$httpCode}", 'ERROR');
            return [];
        }

        $data = json_decode($response, true);
        return $data['data']['bankAccs'] ?? [];
    }

    /**
     * Chuẩn hóa format giao dịch từ Casso
     */
    public function normalizeTransaction($transaction) {
        return [
            'transaction_id' => $transaction['id'] ?? '',
            'amount' => floatval($transaction['amount'] ?? 0),
            'description' => $transaction['description'] ?? '',
            'transaction_date' => isset($transaction['when']) ? 
                date('Y-m-d H:i:s', $transaction['when'] / 1000) : date('Y-m-d H:i:s'),
            'type' => (($transaction['amount'] ?? 0) > 0) ? 'IN' : 'OUT',
            'balance' => floatval($transaction['balance'] ?? 0),
            'bank_account_id' => $transaction['bankSubAccId'] ?? '',
            'bank_name' => $transaction['bank_name'] ?? '',
            'reference_number' => $transaction['tid'] ?? ''
        ];
    }

    /**
     * Parse mã giao dịch từ description
     */
    public function parseTransactionCode($description) {
        // Tìm pattern TSxxxxx trong description
        if (preg_match('/TS\d{5}/', $description, $matches)) {
            return $matches[0];
        }
        return null;
    }

    /**
     * Tạo webhook để nhận callback realtime
     * 
     * @param string $webhookUrl URL webhook của bạn (VD: https://yourdomain.com/webhook_payment.php)
     * @param int $bankAccId ID tài khoản ngân hàng
     */
    public function createWebhook($webhookUrl, $bankAccId = null) {
        if (empty($this->apiKey)) {
            $this->log("API Key chưa được cấu hình", 'ERROR');
            return false;
        }

        $url = $this->apiUrl . '/sync/' . ($bankAccId ?? '0');

        $payload = json_encode([
            'bank_acc_id' => $bankAccId ?? 0,
            'income' => true, // Nhận thông báo tiền vào
            'outcome' => false, // Không nhận thông báo tiền ra
            'url' => $webhookUrl
        ]);

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $payload,
            CURLOPT_HTTPHEADER => [
                'Authorization: Apikey ' . $this->apiKey,
                'Content-Type: application/json'
            ],
            CURLOPT_TIMEOUT => 30
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode === 200) {
            $this->log("Webhook đã được tạo thành công: {$webhookUrl}");
            return true;
        } else {
            $this->log("Tạo webhook thất bại với HTTP code {$httpCode}", 'ERROR');
            return false;
        }
    }

    /**
     * Xác thực webhook callback từ Casso
     */
    public function verifyWebhookSignature($payload, $signature) {
        // Casso không sử dụng signature, thay vào đó check IP whitelist
        // Danh sách IP của Casso (cập nhật từ docs)
        $cassoIPs = [
            '172.105.162.113',
            '139.162.29.153'
        ];

        $clientIP = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? '';
        
        return in_array($clientIP, $cassoIPs);
    }
}

/**
 * Ví dụ sử dụng với Casso
 */
function example_usage() {
    // 1. Lấy danh sách giao dịch
    $casso = new CassoAPI('your-api-key-here');
    
    // Lấy giao dịch 24h gần nhất
    $transactions = $casso->getTransactions();
    
    foreach ($transactions as $tx) {
        $normalized = $casso->normalizeTransaction($tx);
        $code = $casso->parseTransactionCode($normalized['description']);
        
        if ($code) {
            echo "Tìm thấy mã: {$code} - Số tiền: {$normalized['amount']}\n";
        }
    }
    
    // 2. Lấy danh sách tài khoản ngân hàng
    $bankAccounts = $casso->getBankAccounts();
    print_r($bankAccounts);
    
    // 3. Tạo webhook
    $webhookUrl = 'https://yourdomain.com/webhook_payment.php';
    $casso->createWebhook($webhookUrl);
}

?>
