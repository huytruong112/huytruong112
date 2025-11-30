<?php
/**
 * API Webhook nhận thông tin thanh toán từ ngân hàng
 * Endpoint này sẽ nhận POST request từ ngân hàng/cổng thanh toán
 * URL: https://yourdomain.com/api_payment_webhook.php
 */

// Không cần session cho API
header('Content-Type: application/json; charset=utf-8');
date_default_timezone_set('Asia/Ho_Chi_Minh');

require_once 'db.php';
require_once 'payment_helper.php';
require_once 'config_payment.php';

// Chỉ chấp nhận POST request
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'message' => 'Method not allowed'
    ]);
    exit;
}

// Khởi tạo Payment Helper
$paymentHelper = new PaymentHelper($conn);

// Log request để debug
$raw_input = file_get_contents('php://input');
$paymentHelper->logPayment("Webhook nhận request: " . $raw_input);

// 1. Kiểm tra IP (tùy chọn - uncomment nếu muốn giới hạn IP)
/*
$client_ip = $_SERVER['REMOTE_ADDR'] ?? '';
if (!$paymentHelper->isIpAllowed($client_ip)) {
    http_response_code(403);
    echo json_encode([
        'success' => false,
        'message' => 'IP not allowed'
    ]);
    $paymentHelper->logPayment("IP không được phép: $client_ip");
    exit;
}
*/

// 2. Lấy dữ liệu từ request
$content_type = $_SERVER['CONTENT_TYPE'] ?? '';

if (strpos($content_type, 'application/json') !== false) {
    // Nhận JSON data
    $data = json_decode($raw_input, true);
} else {
    // Nhận form data
    $data = $_POST;
}

if (!$data) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'message' => 'Invalid request data'
    ]);
    exit;
}

// 3. Xác thực webhook token (nếu có)
$webhook_token = $data['token'] ?? $_SERVER['HTTP_X_WEBHOOK_TOKEN'] ?? '';
if (WEBHOOK_TOKEN && !$paymentHelper->validateWebhookToken($webhook_token)) {
    http_response_code(401);
    echo json_encode([
        'success' => false,
        'message' => 'Invalid webhook token'
    ]);
    $paymentHelper->logPayment("Token không hợp lệ");
    exit;
}

// 4. Xử lý theo loại webhook
$webhook_type = $data['type'] ?? 'bank_transfer';

switch ($webhook_type) {
    case 'bank_transfer':
        handleBankTransferWebhook($data, $paymentHelper);
        break;
    
    case 'vnpay':
        handleVNPayWebhook($data, $paymentHelper);
        break;
    
    case 'momo':
        handleMomoWebhook($data, $paymentHelper);
        break;
    
    default:
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => 'Unknown webhook type'
        ]);
        break;
}

/**
 * Xử lý webhook từ chuyển khoản ngân hàng
 */
function handleBankTransferWebhook($data, $paymentHelper) {
    try {
        // Lấy thông tin từ webhook
        // Format có thể khác nhau tùy từng ngân hàng/API
        $unique_code = $data['description'] ?? $data['content'] ?? $data['message'] ?? '';
        $amount = (float)($data['amount'] ?? $data['amount_in'] ?? 0);
        $transaction_ref = $data['transaction_id'] ?? $data['ref_no'] ?? $data['reference'] ?? '';
        
        // Thông tin bổ sung
        $extra_data = [
            'bank_name' => $data['bank_name'] ?? '',
            'account_number' => $data['account_number'] ?? '',
            'transaction_date' => $data['transaction_date'] ?? date('Y-m-d H:i:s'),
            'raw_data' => $data
        ];
        
        // Validate dữ liệu cơ bản
        if (empty($unique_code)) {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => 'Missing transaction code'
            ]);
            return;
        }
        
        if ($amount <= 0) {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => 'Invalid amount'
            ]);
            return;
        }
        
        // Xử lý thanh toán tự động
        $result = $paymentHelper->processAutoPayment($unique_code, $amount, $transaction_ref, $extra_data);
        
        if ($result['success']) {
            http_response_code(200);
            echo json_encode([
                'success' => true,
                'message' => 'Payment processed successfully',
                'data' => $result
            ]);
        } else {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => $result['message']
            ]);
        }
        
    } catch (Exception $e) {
        $paymentHelper->logPayment("Lỗi xử lý webhook bank transfer: " . $e->getMessage());
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Internal server error'
        ]);
    }
}

/**
 * Xử lý webhook từ VNPay
 */
function handleVNPayWebhook($data, $paymentHelper) {
    try {
        global $vnpay_config;
        
        // Xác thực chữ ký từ VNPay
        $vnp_SecureHash = $data['vnp_SecureHash'] ?? '';
        unset($data['vnp_SecureHash']);
        
        ksort($data);
        $hashData = "";
        foreach ($data as $key => $value) {
            if (substr($key, 0, 4) == "vnp_") {
                $hashData .= $key . "=" . $value . "&";
            }
        }
        $hashData = rtrim($hashData, "&");
        
        $secureHash = hash_hmac('sha512', $hashData, $vnpay_config['vnp_HashSecret']);
        
        if ($secureHash !== $vnp_SecureHash) {
            http_response_code(401);
            echo json_encode([
                'success' => false,
                'message' => 'Invalid signature'
            ]);
            return;
        }
        
        // Lấy thông tin giao dịch
        $vnp_ResponseCode = $data['vnp_ResponseCode'] ?? '';
        $unique_code = $data['vnp_TxnRef'] ?? '';
        $amount = (float)($data['vnp_Amount'] ?? 0) / 100; // VNPay gửi số tiền x100
        $transaction_ref = $data['vnp_TransactionNo'] ?? '';
        
        // Chỉ xử lý khi thanh toán thành công
        if ($vnp_ResponseCode === '00') {
            $extra_data = [
                'payment_method' => 'vnpay',
                'vnp_data' => $data
            ];
            
            $result = $paymentHelper->processAutoPayment($unique_code, $amount, $transaction_ref, $extra_data);
            
            http_response_code(200);
            echo json_encode([
                'success' => true,
                'message' => 'VNPay payment processed'
            ]);
        } else {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => 'Payment failed with code: ' . $vnp_ResponseCode
            ]);
        }
        
    } catch (Exception $e) {
        $paymentHelper->logPayment("Lỗi xử lý webhook VNPay: " . $e->getMessage());
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Internal server error'
        ]);
    }
}

/**
 * Xử lý webhook từ Momo
 */
function handleMomoWebhook($data, $paymentHelper) {
    try {
        global $momo_config;
        
        // Xác thực chữ ký từ Momo
        $signature = $data['signature'] ?? '';
        $rawHash = "accessKey=" . $momo_config['access_key'] .
                   "&amount=" . ($data['amount'] ?? '') .
                   "&extraData=" . ($data['extraData'] ?? '') .
                   "&message=" . ($data['message'] ?? '') .
                   "&orderId=" . ($data['orderId'] ?? '') .
                   "&orderInfo=" . ($data['orderInfo'] ?? '') .
                   "&orderType=" . ($data['orderType'] ?? '') .
                   "&partnerCode=" . ($data['partnerCode'] ?? '') .
                   "&payType=" . ($data['payType'] ?? '') .
                   "&requestId=" . ($data['requestId'] ?? '') .
                   "&responseTime=" . ($data['responseTime'] ?? '') .
                   "&resultCode=" . ($data['resultCode'] ?? '') .
                   "&transId=" . ($data['transId'] ?? '');
        
        $checkSignature = hash_hmac('sha256', $rawHash, $momo_config['secret_key']);
        
        if ($signature !== $checkSignature) {
            http_response_code(401);
            echo json_encode([
                'success' => false,
                'message' => 'Invalid signature'
            ]);
            return;
        }
        
        // Lấy thông tin giao dịch
        $resultCode = $data['resultCode'] ?? '';
        $unique_code = $data['orderId'] ?? '';
        $amount = (float)($data['amount'] ?? 0);
        $transaction_ref = $data['transId'] ?? '';
        
        // Chỉ xử lý khi thanh toán thành công (resultCode = 0)
        if ($resultCode === '0' || $resultCode === 0) {
            $extra_data = [
                'payment_method' => 'momo',
                'momo_data' => $data
            ];
            
            $result = $paymentHelper->processAutoPayment($unique_code, $amount, $transaction_ref, $extra_data);
            
            http_response_code(200);
            echo json_encode([
                'success' => true,
                'message' => 'Momo payment processed'
            ]);
        } else {
            http_response_code(400);
            echo json_encode([
                'success' => false,
                'message' => 'Payment failed with code: ' . $resultCode
            ]);
        }
        
    } catch (Exception $e) {
        $paymentHelper->logPayment("Lỗi xử lý webhook Momo: " . $e->getMessage());
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Internal server error'
        ]);
    }
}
