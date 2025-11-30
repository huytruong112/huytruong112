<?php
/**
 * API Webhook - Nhận thông báo thanh toán tự động
 * 
 * Endpoint này nhận webhook từ:
 * - Casso.vn
 * - Payos.vn
 * - Các dịch vụ ngân hàng khác
 * 
 * URL: https://yourdomain.com/payment_webhook.php
 * 
 * Cách sử dụng:
 * 1. Đăng ký webhook URL này tại Casso.vn hoặc dịch vụ thanh toán
 * 2. Cấu hình CASSO_API_KEY và CASSO_SECURE_TOKEN trong payment_config.php
 * 3. Khi có giao dịch, Casso sẽ gọi webhook này
 * 4. Script sẽ tự động xử lý và cộng tiền cho user
 */

// Thiết lập múi giờ
date_default_timezone_set('Asia/Ho_Chi_Minh');

// Disable timeout cho webhook
set_time_limit(300); // 5 phút

// Load config và processor
require_once 'payment_config.php';
require_once 'payment_processor.php';

// Kiểm tra xem thanh toán tự động có bật không
if (!PAYMENT_ENABLED) {
    paymentLog("Payment webhook disabled", "WARNING");
    sendJSONResponse([
        'success' => false,
        'message' => 'Payment webhook is disabled'
    ], 503);
}

// Lấy IP của client
$clientIP = getClientIP();
paymentLog("Webhook request from IP: {$clientIP}");

// Kiểm tra IP whitelist
if (!isAllowedIP($clientIP)) {
    paymentLog("IP not allowed: {$clientIP}", "ERROR");
    sendJSONResponse([
        'success' => false,
        'message' => 'Access denied'
    ], 403);
}

// Lấy dữ liệu từ request
$requestMethod = $_SERVER['REQUEST_METHOD'];
$rawInput = file_get_contents('php://input');
paymentLog("Request Method: {$requestMethod}, Raw Input: " . substr($rawInput, 0, 500));

// Parse JSON data
$inputData = json_decode($rawInput, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    paymentLog("Invalid JSON: " . json_last_error_msg(), "ERROR");
    sendJSONResponse([
        'success' => false,
        'message' => 'Invalid JSON format'
    ], 400);
}

// Log request headers (để debug)
if (PAYMENT_DEBUG) {
    $headers = getallheaders();
    paymentLog("Request Headers: " . json_encode($headers, JSON_UNESCAPED_UNICODE));
}

// Kết nối database
require_once 'db.php';
if (!isset($conn)) {
    paymentLog("Database connection failed", "ERROR");
    sendJSONResponse([
        'success' => false,
        'message' => 'Database connection error'
    ], 500);
}

// Khởi tạo processor
$processor = new PaymentProcessor($conn);

// Xác định nguồn webhook và xử lý
$source = $_GET['source'] ?? 'auto'; // Có thể truyền ?source=casso hoặc ?source=payos

// ===== XỬ LÝ CASSO.VN =====
if ($source === 'casso' || (CASSO_ENABLED && isset($inputData['data']))) {
    paymentLog("Xử lý webhook từ Casso.vn");
    
    // Xác thực secure token từ Casso
    $secureToken = $_GET['secure_token'] ?? $_POST['secure_token'] ?? $inputData['secure_token'] ?? '';
    
    if (CASSO_SECURE_TOKEN && $secureToken !== CASSO_SECURE_TOKEN) {
        paymentLog("Invalid Casso secure token: {$secureToken}", "ERROR");
        sendJSONResponse([
            'success' => false,
            'message' => 'Invalid secure token'
        ], 403);
    }
    
    // Kiểm tra duplicate
    foreach ($inputData['data'] as $tx) {
        $refNumber = $tx['tid'] ?? '';
        $amount = $tx['amount'] ?? 0;
        $description = $tx['description'] ?? '';
        
        if ($processor->isDuplicateWebhook($refNumber, $amount, $description)) {
            paymentLog("Duplicate webhook detected: {$refNumber}", "WARNING");
            sendJSONResponse([
                'success' => true,
                'message' => 'Duplicate webhook, already processed'
            ]);
        }
    }
    
    // Xử lý webhook
    $result = $processor->processCassoWebhook($inputData);
    
    sendJSONResponse($result);
}

// ===== XỬ LÝ PAYOS.VN =====
elseif ($source === 'payos' || (PAYOS_ENABLED && isset($inputData['code']))) {
    paymentLog("Xử lý webhook từ Payos.vn");
    
    // Xác thực signature từ Payos
    // TODO: Implement Payos signature verification
    
    $result = $processor->processPayosWebhook($inputData);
    sendJSONResponse($result);
}

// ===== XỬ LÝ WEBHOOK CHUNG =====
elseif ($source === 'generic' || isset($inputData['amount'])) {
    paymentLog("Xử lý generic webhook");
    
    // Xác thực secret key
    $providedSecret = $_GET['secret'] ?? $_POST['secret'] ?? $inputData['secret'] ?? '';
    if ($providedSecret !== WEBHOOK_SECRET) {
        paymentLog("Invalid webhook secret", "ERROR");
        sendJSONResponse([
            'success' => false,
            'message' => 'Invalid secret key'
        ], 403);
    }
    
    // Xử lý giao dịch
    $result = $processor->processTransaction([
        'amount' => $inputData['amount'] ?? 0,
        'description' => $inputData['description'] ?? '',
        'transaction_date' => $inputData['transaction_date'] ?? date('Y-m-d H:i:s'),
        'reference_number' => $inputData['reference'] ?? uniqid(),
        'source' => $inputData['source'] ?? 'generic'
    ]);
    
    sendJSONResponse($result);
}

// ===== XỬ LÝ TEST WEBHOOK (CHỈ DÙNG KHI DEBUG) =====
elseif (PAYMENT_DEBUG && $requestMethod === 'GET' && isset($_GET['test'])) {
    paymentLog("Test webhook được gọi");
    
    sendJSONResponse([
        'success' => true,
        'message' => 'Webhook is working',
        'server_time' => date('Y-m-d H:i:s'),
        'ip' => $clientIP,
        'config' => [
            'casso_enabled' => CASSO_ENABLED,
            'payos_enabled' => PAYOS_ENABLED,
            'allowed_ips' => ALLOWED_IPS
        ]
    ]);
}

// ===== KHÔNG XÁC ĐỊNH ĐƯỢC NGUỒN =====
else {
    paymentLog("Unknown webhook source or invalid data", "WARNING");
    sendJSONResponse([
        'success' => false,
        'message' => 'Unknown webhook source or invalid data format',
        'hint' => 'Please specify ?source=casso or ?source=payos or provide valid data'
    ], 400);
}
