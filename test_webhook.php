<?php
/**
 * Script test webhook thanh toán
 * Dùng để test webhook locally mà không cần service thật
 */

// URL webhook của bạn
$webhook_url = 'http://localhost/api_payment_webhook.php'; // Thay đổi thành URL thật

// Test cases
$test_cases = [
    [
        'name' => 'Test 1: Giao dịch hợp lệ',
        'payload' => [
            'transaction_id' => 'TEST001',
            'amount' => 100000,
            'description' => 'TS12345 Nap tien',
            'date' => date('Y-m-d H:i:s')
        ],
        'expect' => 'success'
    ],
    [
        'name' => 'Test 2: Mã viết thường',
        'payload' => [
            'transaction_id' => 'TEST002',
            'amount' => 50000,
            'description' => 'ts67890 nap tien test',
            'date' => date('Y-m-d H:i:s')
        ],
        'expect' => 'success'
    ],
    [
        'name' => 'Test 3: Mã có khoảng trắng',
        'payload' => [
            'transaction_id' => 'TEST003',
            'amount' => 200000,
            'description' => 'Chuyen khoan TS 11111 cho toi nhe',
            'date' => date('Y-m-d H:i:s')
        ],
        'expect' => 'success'
    ],
    [
        'name' => 'Test 4: Không có mã',
        'payload' => [
            'transaction_id' => 'TEST004',
            'amount' => 100000,
            'description' => 'Chuyen tien khong co ma',
            'date' => date('Y-m-d H:i:s')
        ],
        'expect' => 'fail'
    ],
    [
        'name' => 'Test 5: Số tiền = 0',
        'payload' => [
            'transaction_id' => 'TEST005',
            'amount' => 0,
            'description' => 'TS99999',
            'date' => date('Y-m-d H:i:s')
        ],
        'expect' => 'fail'
    ],
    [
        'name' => 'Test 6: Format Casso',
        'payload' => [
            'id' => 123456,
            'tid' => 'FT21123456789',
            'description' => 'TS22222 NGUYEN VAN A chuyen tien',
            'amount' => 150000,
            'when' => date('Y-m-d H:i:s')
        ],
        'expect' => 'success'
    ],
];

echo "=================================\n";
echo "  TEST WEBHOOK THANH TOÁN\n";
echo "=================================\n\n";

echo "URL: {$webhook_url}\n";
echo "Số test: " . count($test_cases) . "\n\n";

$passed = 0;
$failed = 0;

foreach ($test_cases as $i => $test) {
    echo "--- Test " . ($i + 1) . ": {$test['name']} ---\n";
    
    // Gửi request
    $ch = curl_init($webhook_url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($test['payload']));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        echo "❌ CURL Error: {$error}\n\n";
        $failed++;
        continue;
    }
    
    echo "HTTP Code: {$http_code}\n";
    echo "Response: {$response}\n";
    
    $result = json_decode($response, true);
    
    if ($result && isset($result['success'])) {
        $success = $result['success'];
        
        if (($test['expect'] === 'success' && $success) || ($test['expect'] === 'fail' && !$success)) {
            echo "✅ PASSED\n";
            $passed++;
        } else {
            echo "❌ FAILED (Expected: {$test['expect']}, Got: " . ($success ? 'success' : 'fail') . ")\n";
            $failed++;
        }
    } else {
        echo "❌ FAILED (Invalid response)\n";
        $failed++;
    }
    
    echo "\n";
}

echo "=================================\n";
echo "KẾT QUẢ:\n";
echo "✅ Passed: {$passed}\n";
echo "❌ Failed: {$failed}\n";
echo "=================================\n";
