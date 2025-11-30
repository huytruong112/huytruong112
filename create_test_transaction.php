<?php
/**
 * Script tạo giao dịch test trong database
 * Chạy script này trước khi test webhook
 */

require_once __DIR__ . '/db.php';

echo "=================================\n";
echo "  TẠO GIAO DỊCH TEST\n";
echo "=================================\n\n";

// Lấy user_id đầu tiên trong DB (hoặc thay bằng user_id thật)
$result = $conn->query("SELECT id, username FROM users LIMIT 1");
if ($result->num_rows === 0) {
    die("❌ Không tìm thấy user nào trong database!\n");
}

$user = $result->fetch_assoc();
$user_id = $user['id'];
$username = $user['username'];

echo "User ID: {$user_id} ({$username})\n\n";

// Tạo các giao dịch test
$test_transactions = [
    ['code' => 'TS12345', 'amount' => 100000],
    ['code' => 'TS67890', 'amount' => 50000],
    ['code' => 'TS11111', 'amount' => 200000],
    ['code' => 'TS22222', 'amount' => 150000],
    ['code' => 'TS99999', 'amount' => 75000],
];

echo "Tạo " . count($test_transactions) . " giao dịch test...\n\n";

$created = 0;
foreach ($test_transactions as $tx) {
    // Kiểm tra đã tồn tại chưa
    $stmt = $conn->prepare("SELECT transaction_id FROM transactions WHERE unique_code = ? LIMIT 1");
    $stmt->bind_param("s", $tx['code']);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows > 0) {
        echo "⚠️  {$tx['code']}: Đã tồn tại, bỏ qua\n";
        continue;
    }
    
    // Tạo mới
    $stmt = $conn->prepare(
        "INSERT INTO transactions (user_id, amount_paid, unique_code, status, transaction_date, description)
         VALUES (?, ?, ?, 'pending', NOW(), 'Test transaction')"
    );
    $stmt->bind_param("ids", $user_id, $tx['amount'], $tx['code']);
    
    if ($stmt->execute()) {
        echo "✅ {$tx['code']}: Tạo thành công (Số tiền: " . number_format($tx['amount']) . " VND)\n";
        $created++;
    } else {
        echo "❌ {$tx['code']}: Lỗi - " . $stmt->error . "\n";
    }
}

echo "\n=================================\n";
echo "Đã tạo: {$created} giao dịch\n";
echo "=================================\n\n";

echo "Bây giờ bạn có thể chạy test_webhook.php để test!\n";
