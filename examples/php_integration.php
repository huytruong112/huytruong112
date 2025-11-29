<?php
/**
 * Ví dụ tích hợp VPN API với PHP
 * 
 * Sử dụng khi khách hàng thanh toán thành công trên website
 */

class VPNAPIClient {
    private $apiUrl;
    private $apiKey;
    
    public function __construct($apiUrl, $apiKey) {
        $this->apiUrl = rtrim($apiUrl, '/');
        $this->apiKey = $apiKey;
    }
    
    /**
     * Đăng ký khách hàng mới
     */
    public function registerCustomer($email, $name, $plan, $phone = null) {
        $url = $this->apiUrl . '/api/v1/customer/register';
        
        $data = [
            'email' => $email,
            'name' => $name,
            'plan' => $plan,
            'phone' => $phone
        ];
        
        return $this->makeRequest('POST', $url, $data);
    }
    
    /**
     * Lấy thông tin usage của khách hàng
     */
    public function getCustomerUsage($email, $panelName = null) {
        $url = $this->apiUrl . '/api/v1/customer/usage';
        
        $data = [
            'email' => $email,
            'panel_name' => $panelName
        ];
        
        return $this->makeRequest('POST', $url, $data);
    }
    
    /**
     * Gia hạn dịch vụ
     */
    public function renewCustomer($email, $panelName, $days = 30) {
        $url = $this->apiUrl . '/api/v1/customer/renew';
        
        $data = [
            'email' => $email,
            'panel_name' => $panelName,
            'days' => $days
        ];
        
        return $this->makeRequest('POST', $url, $data);
    }
    
    /**
     * Xóa khách hàng
     */
    public function deleteCustomer($email, $panelName, $inboundId = null) {
        $url = $this->apiUrl . '/api/v1/customer/delete';
        
        $data = [
            'email' => $email,
            'panel_name' => $panelName,
            'inbound_id' => $inboundId
        ];
        
        return $this->makeRequest('DELETE', $url, $data);
    }
    
    /**
     * Lấy danh sách plans
     */
    public function getPlans() {
        $url = $this->apiUrl . '/api/v1/plans';
        return $this->makeRequest('GET', $url);
    }
    
    /**
     * Thực hiện HTTP request
     */
    private function makeRequest($method, $url, $data = null) {
        $headers = [
            "Content-Type: application/json",
            "X-API-Key: {$this->apiKey}"
        ];
        
        $options = [
            'http' => [
                'header' => implode("\r\n", $headers),
                'method' => $method,
                'ignore_errors' => true
            ]
        ];
        
        if ($data !== null && in_array($method, ['POST', 'PUT', 'DELETE'])) {
            $options['http']['content'] = json_encode($data);
        }
        
        $context = stream_context_create($options);
        $result = @file_get_contents($url, false, $context);
        
        if ($result === false) {
            return [
                'success' => false,
                'error' => 'Failed to connect to API'
            ];
        }
        
        return json_decode($result, true);
    }
}

// ============================================
// Ví dụ sử dụng
// ============================================

// Khởi tạo client
$vpnApi = new VPNAPIClient(
    'http://your-api-server:8000',
    'your_secret_api_key_here'
);

// Ví dụ 1: Đăng ký khách hàng mới sau khi thanh toán thành công
function processPaymentSuccess($orderId, $customerEmail, $customerName, $plan) {
    global $vpnApi;
    
    // Đăng ký VPN cho khách hàng
    $result = $vpnApi->registerCustomer(
        $customerEmail,
        $customerName,
        $plan
    );
    
    if ($result['success']) {
        // Lưu thông tin vào database
        saveVPNInfo($orderId, $customerEmail, $result['data']);
        
        // Gửi email cho khách hàng với thông tin VPN
        sendVPNEmail($customerEmail, $result['data']);
        
        return true;
    } else {
        // Log lỗi
        error_log("Failed to create VPN for order $orderId: " . json_encode($result));
        return false;
    }
}

// Ví dụ 2: Kiểm tra usage của khách hàng
function checkCustomerUsage($email) {
    global $vpnApi;
    
    $usage = $vpnApi->getCustomerUsage($email);
    
    if ($usage['success']) {
        $data = $usage['data'];
        
        // Hiển thị thông tin
        echo "Email: " . $email . "\n";
        echo "Data used: " . formatBytes($data['up'] + $data['down']) . "\n";
        echo "Total data: " . formatBytes($data['total']) . "\n";
        echo "Expiry: " . date('Y-m-d H:i:s', $data['expiryTime'] / 1000) . "\n";
        
        // Cảnh báo nếu sắp hết dung lượng
        $usedPercent = (($data['up'] + $data['down']) / $data['total']) * 100;
        if ($usedPercent > 80) {
            sendWarningEmail($email, "Bạn đã sử dụng $usedPercent% dung lượng");
        }
    }
}

// Ví dụ 3: Gia hạn tự động khi thanh toán gia hạn
function processRenewalPayment($customerEmail, $panelName, $months = 1) {
    global $vpnApi;
    
    $days = $months * 30;
    $result = $vpnApi->renewCustomer($customerEmail, $panelName, $days);
    
    if ($result['success']) {
        // Cập nhật database
        updateRenewalDate($customerEmail, $days);
        
        // Gửi email xác nhận
        sendRenewalConfirmation($customerEmail, $days);
        
        return true;
    }
    
    return false;
}

// Ví dụ 4: Webhook khi nhận thanh toán từ payment gateway
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_GET['webhook'])) {
    // Verify webhook signature (tùy payment gateway)
    
    $payload = json_decode(file_get_contents('php://input'), true);
    
    if ($payload['status'] === 'success') {
        $email = $payload['customer_email'];
        $name = $payload['customer_name'];
        $plan = $payload['plan']; // basic, premium, enterprise
        
        // Tạo VPN tự động
        $result = $vpnApi->registerCustomer($email, $name, $plan);
        
        if ($result['success']) {
            // Trả về success cho payment gateway
            http_response_code(200);
            echo json_encode(['status' => 'ok']);
        } else {
            // Log và retry sau
            http_response_code(500);
            echo json_encode(['status' => 'error', 'message' => 'Failed to create VPN']);
        }
    }
}

// Helper functions
function formatBytes($bytes) {
    if ($bytes >= 1073741824) {
        return number_format($bytes / 1073741824, 2) . ' GB';
    } elseif ($bytes >= 1048576) {
        return number_format($bytes / 1048576, 2) . ' MB';
    } elseif ($bytes >= 1024) {
        return number_format($bytes / 1024, 2) . ' KB';
    } else {
        return $bytes . ' bytes';
    }
}

function saveVPNInfo($orderId, $email, $vpnData) {
    // Implement database save
    // Example: mysqli_query($conn, "INSERT INTO vpn_configs ...");
}

function sendVPNEmail($email, $vpnData) {
    // Implement email sending
    // Example: mail($email, "Your VPN Config", ...);
}

function sendWarningEmail($email, $message) {
    // Implement warning email
}

function updateRenewalDate($email, $days) {
    // Update database
}

function sendRenewalConfirmation($email, $days) {
    // Send confirmation email
}
?>
