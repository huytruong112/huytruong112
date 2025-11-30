<?php
/**
 * File test webhook - Dùng để test API thanh toán tự động
 * 
 * Cách dùng:
 * 1. Tạo một giao dịch pending trong database với mã TSxxxxx
 * 2. Chạy file này để giả lập webhook từ ngân hàng
 * 3. Kiểm tra xem giao dịch có được cập nhật tự động không
 */

// Cấu hình
$webhookUrl = 'http://localhost/payment_webhook.php?source=generic&secret=your-secret-key-change-this-' . md5('vpn-vietnam');

// Dữ liệu test
$testData = [
    'amount' => 100000, // 100k VND
    'description' => 'Chuyen tien TS12345', // Thay TS12345 bằng mã giao dịch thực tế
    'transaction_date' => date('Y-m-d H:i:s'),
    'reference' => 'TEST_' . time(),
    'source' => 'test'
];

echo "=== TEST WEBHOOK ===\n";
echo "URL: {$webhookUrl}\n";
echo "Data: " . json_encode($testData, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . "\n\n";

// Gửi request
$ch = curl_init($webhookUrl);
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode($testData),
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'User-Agent: Test-Webhook/1.0'
    ],
    CURLOPT_TIMEOUT => 30
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

echo "=== RESPONSE ===\n";
echo "HTTP Code: {$httpCode}\n";

if ($error) {
    echo "Error: {$error}\n";
} else {
    echo "Response: " . $response . "\n";
    
    // Parse JSON
    $result = json_decode($response, true);
    if ($result) {
        echo "\n=== PARSED RESULT ===\n";
        print_r($result);
        
        if (isset($result['success']) && $result['success']) {
            echo "\n✓ TEST THÀNH CÔNG!\n";
        } else {
            echo "\n✗ TEST THẤT BẠI!\n";
            echo "Message: " . ($result['message'] ?? 'Unknown error') . "\n";
        }
    }
}

echo "\n=== HƯỚNG DẪN ===\n";
echo "1. Nếu báo 'Transaction not found', hãy tạo giao dịch với mã TS12345 trước\n";
echo "2. Nếu báo 'Invalid secret key', kiểm tra WEBHOOK_SECRET trong payment_config.php\n";
echo "3. Nếu báo 'Access denied', kiểm tra ALLOWED_IPS trong payment_config.php\n";
echo "4. Kiểm tra file log tại logs/payment_webhook.log để xem chi tiết\n";
