<?php
/**
 * Script test webhook thanh toán
 * File này dùng để test API webhook có hoạt động đúng không
 * 
 * Cách sử dụng:
 * 1. Chỉnh sửa thông tin test ở dưới
 * 2. Chạy: php test_webhook.php
 * 3. Hoặc truy cập: https://yourdomain.com/test_webhook.php
 */

date_default_timezone_set('Asia/Ho_Chi_Minh');

echo "<h1>Test Webhook Thanh Toán Tự Động</h1>";
echo "<pre>";

// Cấu hình test
$webhook_url = 'http://localhost/api_payment_webhook.php'; // Thay đổi URL này
$webhook_token = 'your-webhook-token-here-change-this'; // Token từ config_payment.php

// Dữ liệu test - thay đổi theo giao dịch thực tế
$test_data = [
    'type' => 'bank_transfer', // bank_transfer, vnpay, momo
    'token' => $webhook_token,
    'description' => 'TS00001', // Mã giao dịch (unique_code) từ hệ thống
    'amount' => 100000, // Số tiền
    'transaction_id' => 'BANK_' . time(), // Mã tham chiếu từ ngân hàng
    'bank_name' => 'MB Bank',
    'account_number' => '0123456789',
    'transaction_date' => date('Y-m-d H:i:s')
];

echo "========================================\n";
echo "THÔNG TIN TEST\n";
echo "========================================\n";
echo "Webhook URL: $webhook_url\n";
echo "Mã giao dịch: {$test_data['description']}\n";
echo "Số tiền: " . number_format($test_data['amount'], 0, ',', '.') . " VND\n";
echo "Loại: {$test_data['type']}\n";
echo "\n";

// Gửi request
echo "Đang gửi request...\n\n";

$ch = curl_init($webhook_url);
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode($test_data),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'X-Webhook-Token: ' . $webhook_token
    ],
    CURLOPT_TIMEOUT => 30
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

echo "========================================\n";
echo "KẾT QUẢ\n";
echo "========================================\n";

if ($error) {
    echo "❌ Lỗi cURL: $error\n";
} else {
    echo "HTTP Code: $http_code\n";
    echo "Response:\n";
    
    $response_data = json_decode($response, true);
    if ($response_data) {
        echo json_encode($response_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    } else {
        echo $response;
    }
    echo "\n\n";
    
    if ($http_code == 200 && isset($response_data['success']) && $response_data['success']) {
        echo "✓✓✓ TEST THÀNH CÔNG! ✓✓✓\n";
    } else {
        echo "✗✗✗ TEST THẤT BẠI! ✗✗✗\n";
    }
}

echo "\n========================================\n";
echo "Kiểm tra thêm:\n";
echo "1. Xem file log: logs/payment.log\n";
echo "2. Kiểm tra database: bảng transactions và payment_logs\n";
echo "3. Kiểm tra số dư user đã tăng chưa\n";
echo "========================================\n";

echo "</pre>";
