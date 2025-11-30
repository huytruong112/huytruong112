<?php
/**
 * Script đồng bộ lịch sử giao dịch từ Casso.vn
 * 
 * Dùng để sync lại các giao dịch cũ hoặc giao dịch bị miss webhook
 * 
 * Sử dụng:
 * php casso_sync.php [from_date] [to_date]
 * 
 * Ví dụ:
 * php casso_sync.php 2025-11-01 2025-11-30
 */

date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once __DIR__ . '/payment_config.php';
require_once __DIR__ . '/payment_processor.php';
require_once __DIR__ . '/db.php';

// Kiểm tra Casso có được bật không
if (!CASSO_ENABLED) {
    die("Casso.vn integration is not enabled. Check payment_config.php\n");
}

if (!CASSO_API_KEY || CASSO_API_KEY === 'YOUR_CASSO_API_KEY_HERE') {
    die("Please configure CASSO_API_KEY in payment_config.php\n");
}

// Lấy tham số ngày
$fromDate = $argv[1] ?? date('Y-m-d', strtotime('-7 days')); // Mặc định 7 ngày trước
$toDate = $argv[2] ?? date('Y-m-d'); // Mặc định hôm nay

echo "=== CASSO SYNC TOOL ===\n";
echo "From: {$fromDate}\n";
echo "To: {$toDate}\n\n";

// Chuyển đổi sang timestamp
$fromTimestamp = strtotime($fromDate . ' 00:00:00');
$toTimestamp = strtotime($toDate . ' 23:59:59');

// Gọi API Casso để lấy lịch sử giao dịch
$apiUrl = "https://oauth.casso.vn/v2/transactions";
$apiUrl .= "?fromDate=" . $fromTimestamp;
$apiUrl .= "&toDate=" . $toTimestamp;
$apiUrl .= "&pageSize=100";

echo "Fetching transactions from Casso API...\n";

$ch = curl_init($apiUrl);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        'Authorization: Apikey ' . CASSO_API_KEY,
        'Content-Type: application/json'
    ],
    CURLOPT_TIMEOUT => 60
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    die("CURL Error: {$error}\n");
}

if ($httpCode !== 200) {
    die("API Error: HTTP {$httpCode}\nResponse: {$response}\n");
}

$data = json_decode($response, true);

if (!isset($data['data']) || !isset($data['data']['records'])) {
    die("Invalid API response format\n");
}

$transactions = $data['data']['records'];
$totalCount = count($transactions);

echo "Found {$totalCount} transaction(s) from Casso\n\n";

if ($totalCount === 0) {
    echo "No transactions to process\n";
    exit(0);
}

// Khởi tạo processor
$processor = new PaymentProcessor($conn);

$successCount = 0;
$failedCount = 0;
$skippedCount = 0;

foreach ($transactions as $index => $tx) {
    $index++;
    echo "[{$index}/{$totalCount}] Processing transaction ID: " . ($tx['id'] ?? 'N/A') . "\n";
    
    // Kiểm tra duplicate
    if ($processor->isDuplicateWebhook($tx['tid'] ?? '', $tx['amount'] ?? 0, $tx['description'] ?? '')) {
        echo "  → Skipped (duplicate)\n";
        $skippedCount++;
        continue;
    }
    
    // Xử lý giao dịch
    $result = $processor->processTransaction([
        'amount' => $tx['amount'] ?? 0,
        'description' => $tx['description'] ?? '',
        'transaction_date' => date('Y-m-d H:i:s', $tx['when'] ?? time()),
        'reference_number' => $tx['tid'] ?? '',
        'bank_account' => $tx['bank_sub_acc_id'] ?? '',
        'source' => 'casso_sync'
    ]);
    
    if ($result['success']) {
        echo "  → Success: " . ($result['message'] ?? 'OK') . "\n";
        $successCount++;
    } else {
        echo "  → Failed: " . ($result['message'] ?? 'Unknown error') . "\n";
        $failedCount++;
    }
    
    // Sleep để tránh quá tải
    usleep(100000); // 0.1 giây
}

echo "\n=== SYNC COMPLETED ===\n";
echo "Total: {$totalCount}\n";
echo "Success: {$successCount}\n";
echo "Failed: {$failedCount}\n";
echo "Skipped: {$skippedCount}\n";
