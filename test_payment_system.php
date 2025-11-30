#!/usr/bin/env php
<?php
/**
 * Test Payment System
 * Script test các chức năng của hệ thống thanh toán
 * 
 * Chạy: php test_payment_system.php
 */

require_once __DIR__ . '/db.php';
require_once __DIR__ . '/bank_api_casso.php';
require_once __DIR__ . '/auto_payment_check_casso.php';
require_once __DIR__ . '/payment_config.php';

echo "\n";
echo "========================================\n";
echo "    TEST HỆ THỐNG THANH TOÁN TỰ ĐỘNG   \n";
echo "========================================\n\n";

$allTestsPassed = true;

// Test 1: Database Connection
echo "[TEST 1/8] Kiểm tra kết nối database...\n";
try {
    if ($conn && $conn->ping()) {
        echo "✅ PASS: Kết nối database thành công\n";
    } else {
        echo "❌ FAIL: Không thể kết nối database\n";
        $allTestsPassed = false;
    }
} catch (Exception $e) {
    echo "❌ FAIL: Lỗi kết nối database: " . $e->getMessage() . "\n";
    $allTestsPassed = false;
}
echo "\n";

// Test 2: Check Tables
echo "[TEST 2/8] Kiểm tra bảng transactions...\n";
try {
    $result = $conn->query("SHOW TABLES LIKE 'transactions'");
    if ($result && $result->num_rows > 0) {
        echo "✅ PASS: Bảng transactions tồn tại\n";
        
        // Check updated_at column
        $result = $conn->query("SHOW COLUMNS FROM transactions LIKE 'updated_at'");
        if ($result && $result->num_rows > 0) {
            echo "✅ PASS: Cột updated_at đã tồn tại\n";
        } else {
            echo "⚠️  WARNING: Cột updated_at chưa tồn tại - chạy db_schema.sql\n";
        }
    } else {
        echo "❌ FAIL: Bảng transactions không tồn tại\n";
        $allTestsPassed = false;
    }
} catch (Exception $e) {
    echo "❌ FAIL: Lỗi: " . $e->getMessage() . "\n";
    $allTestsPassed = false;
}
echo "\n";

// Test 3: Check Config
echo "[TEST 3/8] Kiểm tra cấu hình...\n";
$configIssues = [];

if (!defined('PAYMENT_AUTO_CHECK_ENABLED')) {
    $configIssues[] = "PAYMENT_AUTO_CHECK_ENABLED không được định nghĩa";
}

if (defined('WEBHOOK_SECRET') && WEBHOOK_SECRET === 'your-webhook-secret-key-change-this') {
    $configIssues[] = "WEBHOOK_SECRET chưa được đổi";
}

if (defined('PAYMENT_API_SECRET') && PAYMENT_API_SECRET === 'your-api-secret-key-change-this') {
    $configIssues[] = "PAYMENT_API_SECRET chưa được đổi";
}

if (empty($configIssues)) {
    echo "✅ PASS: Cấu hình hợp lệ\n";
} else {
    echo "⚠️  WARNING: Có vấn đề với cấu hình:\n";
    foreach ($configIssues as $issue) {
        echo "   - {$issue}\n";
    }
}
echo "\n";

// Test 4: Check Casso API (nếu được cấu hình)
echo "[TEST 4/8] Kiểm tra Casso API...\n";
if (USE_COMMUNITY_API && !empty(COMMUNITY_API_KEY)) {
    try {
        $casso = new CassoAPI();
        $bankAccounts = $casso->getBankAccounts();
        
        if (!empty($bankAccounts)) {
            echo "✅ PASS: Kết nối Casso thành công\n";
            echo "   Tài khoản: " . count($bankAccounts) . " ngân hàng\n";
            foreach ($bankAccounts as $acc) {
                echo "   - {$acc['bankName']} - {$acc['bankAccountNumber']}\n";
            }
        } else {
            echo "⚠️  WARNING: Kết nối Casso OK nhưng không có tài khoản ngân hàng\n";
        }
    } catch (Exception $e) {
        echo "❌ FAIL: Lỗi kết nối Casso: " . $e->getMessage() . "\n";
        $allTestsPassed = false;
    }
} else {
    echo "⚠️  SKIP: Casso chưa được cấu hình (USE_COMMUNITY_API = false hoặc không có API key)\n";
}
echo "\n";

// Test 5: Test Transaction Code Parser
echo "[TEST 5/8] Kiểm tra parse mã giao dịch...\n";
$testDescriptions = [
    'TS12345 Nap tien' => 'TS12345',
    'Chuyen tien TS99999' => 'TS99999',
    'TS00001 test' => 'TS00001',
    'No code here' => null
];

$parseTestPassed = true;
$casso = new CassoAPI();

foreach ($testDescriptions as $desc => $expected) {
    $result = $casso->parseTransactionCode($desc);
    if ($result === $expected) {
        echo "✅ PASS: '{$desc}' => " . ($result ?? 'null') . "\n";
    } else {
        echo "❌ FAIL: '{$desc}' => Expected: " . ($expected ?? 'null') . ", Got: " . ($result ?? 'null') . "\n";
        $parseTestPassed = false;
    }
}

if ($parseTestPassed) {
    echo "✅ PASS: Tất cả test parse đều OK\n";
} else {
    $allTestsPassed = false;
}
echo "\n";

// Test 6: Check Log Directory
echo "[TEST 6/8] Kiểm tra thư mục logs...\n";
$logDir = __DIR__ . '/logs';
if (file_exists($logDir) && is_dir($logDir)) {
    echo "✅ PASS: Thư mục logs tồn tại\n";
    
    if (is_writable($logDir)) {
        echo "✅ PASS: Thư mục logs có thể ghi được\n";
    } else {
        echo "❌ FAIL: Thư mục logs không thể ghi - chạy: chmod 755 logs\n";
        $allTestsPassed = false;
    }
} else {
    echo "❌ FAIL: Thư mục logs không tồn tại - tạo: mkdir -p logs\n";
    $allTestsPassed = false;
}
echo "\n";

// Test 7: Test Pending Transactions Query
echo "[TEST 7/8] Kiểm tra query giao dịch pending...\n";
try {
    $sql = "SELECT COUNT(*) as count FROM transactions WHERE status = 'pending' AND transaction_date > DATE_SUB(NOW(), INTERVAL 24 HOUR)";
    $result = $conn->query($sql);
    $row = $result->fetch_assoc();
    
    echo "✅ PASS: Query thành công\n";
    echo "   Số giao dịch pending (24h): {$row['count']}\n";
} catch (Exception $e) {
    echo "❌ FAIL: Lỗi query: " . $e->getMessage() . "\n";
    $allTestsPassed = false;
}
echo "\n";

// Test 8: Test AutoPaymentProcessor
echo "[TEST 8/8] Kiểm tra AutoPaymentProcessor...\n";
try {
    $processor = new AutoPaymentProcessorCasso($conn);
    echo "✅ PASS: Khởi tạo processor thành công\n";
    
    // Test check single transaction (với mã không tồn tại)
    $result = $processor->checkSingleTransaction('TS99999');
    if (isset($result['success'])) {
        echo "✅ PASS: Hàm checkSingleTransaction hoạt động OK\n";
    }
} catch (Exception $e) {
    echo "❌ FAIL: Lỗi: " . $e->getMessage() . "\n";
    $allTestsPassed = false;
}
echo "\n";

// Summary
echo "========================================\n";
echo "              KẾT QUẢ TEST             \n";
echo "========================================\n\n";

if ($allTestsPassed) {
    echo "✅ TẤT CẢ TEST ĐỀU PASS!\n\n";
    echo "Hệ thống sẵn sàng hoạt động.\n\n";
    echo "Các bước tiếp theo:\n";
    echo "1. Cấu hình cronjob:\n";
    echo "   crontab -e\n";
    echo "   */1 * * * * /usr/bin/php " . __DIR__ . "/cron_check_payment_casso.php\n\n";
    echo "2. Test bằng giao dịch thật\n\n";
    echo "3. Monitor logs:\n";
    echo "   tail -f logs/payment.log\n";
    echo "   tail -f logs/cron.log\n\n";
} else {
    echo "❌ CÓ MỘT SỐ TEST THẤT BẠI\n\n";
    echo "Vui lòng kiểm tra và sửa các lỗi trên trước khi sử dụng.\n\n";
}

echo "========================================\n";

exit($allTestsPassed ? 0 : 1);

?>
