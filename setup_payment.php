#!/usr/bin/env php
<?php
/**
 * Setup Script - Cài đặt hệ thống thanh toán tự động
 * 
 * Chạy: php setup_payment.php
 */

echo "========================================\n";
echo "  Cài Đặt Hệ Thống Thanh Toán Tự Động  \n";
echo "========================================\n\n";

// 1. Check PHP version
echo "[1/7] Kiểm tra PHP version...\n";
$phpVersion = phpversion();
if (version_compare($phpVersion, '7.4.0', '<')) {
    die("❌ PHP version phải >= 7.4.0 (hiện tại: {$phpVersion})\n");
}
echo "✅ PHP version: {$phpVersion}\n\n";

// 2. Check required extensions
echo "[2/7] Kiểm tra PHP extensions...\n";
$requiredExtensions = ['mysqli', 'curl', 'json', 'mbstring'];
$missingExtensions = [];
foreach ($requiredExtensions as $ext) {
    if (!extension_loaded($ext)) {
        $missingExtensions[] = $ext;
        echo "❌ Extension {$ext} không được cài đặt\n";
    } else {
        echo "✅ Extension {$ext}\n";
    }
}
if (!empty($missingExtensions)) {
    die("\n❌ Vui lòng cài đặt các extension còn thiếu\n");
}
echo "\n";

// 3. Create directories
echo "[3/7] Tạo thư mục logs...\n";
$logDir = __DIR__ . '/logs';
if (!file_exists($logDir)) {
    if (mkdir($logDir, 0755, true)) {
        echo "✅ Đã tạo thư mục: {$logDir}\n";
    } else {
        die("❌ Không thể tạo thư mục logs\n");
    }
} else {
    echo "✅ Thư mục logs đã tồn tại\n";
}

// Create .gitignore for logs
file_put_contents($logDir . '/.gitignore', "*.log\n*.lock\n");
echo "✅ Đã tạo .gitignore cho logs\n\n";

// 4. Set permissions
echo "[4/7] Phân quyền files...\n";
$filesToChmod = [
    __DIR__ . '/cron_check_payment.php' => 0755,
    __DIR__ . '/logs' => 0755
];

foreach ($filesToChmod as $file => $perm) {
    if (file_exists($file)) {
        chmod($file, $perm);
        echo "✅ Đã chmod " . decoct($perm) . ": {$file}\n";
    }
}
echo "\n";

// 5. Check database connection
echo "[5/7] Kiểm tra kết nối database...\n";
if (file_exists(__DIR__ . '/db.php')) {
    require_once __DIR__ . '/db.php';
    if (isset($conn) && $conn->ping()) {
        echo "✅ Kết nối database thành công\n";
        
        // Check if transactions table exists
        $result = $conn->query("SHOW TABLES LIKE 'transactions'");
        if ($result && $result->num_rows > 0) {
            echo "✅ Bảng transactions tồn tại\n";
            
            // Check if updated_at column exists
            $result = $conn->query("SHOW COLUMNS FROM transactions LIKE 'updated_at'");
            if ($result && $result->num_rows > 0) {
                echo "✅ Cột updated_at đã tồn tại\n";
            } else {
                echo "⚠️  Cột updated_at chưa tồn tại - cần chạy db_schema.sql\n";
            }
        } else {
            echo "⚠️  Bảng transactions không tồn tại - cần tạo schema\n";
        }
    } else {
        echo "❌ Không thể kết nối database\n";
    }
} else {
    echo "⚠️  File db.php không tồn tại - bỏ qua kiểm tra database\n";
}
echo "\n";

// 6. Check config
echo "[6/7] Kiểm tra cấu hình...\n";
if (file_exists(__DIR__ . '/payment_config.php')) {
    require_once __DIR__ . '/payment_config.php';
    
    // Check if default secrets have been changed
    $warnings = [];
    
    if (WEBHOOK_SECRET === 'your-webhook-secret-key-change-this') {
        $warnings[] = "WEBHOOK_SECRET chưa được đổi";
    }
    
    if (PAYMENT_API_SECRET === 'your-api-secret-key-change-this') {
        $warnings[] = "PAYMENT_API_SECRET chưa được đổi";
    }
    
    if (BANK_API_TYPE === 'vcb' && empty(VCB_USERNAME)) {
        $warnings[] = "Chưa cấu hình thông tin ngân hàng";
    }
    
    if (!empty($warnings)) {
        echo "⚠️  Cần cấu hình trong payment_config.php:\n";
        foreach ($warnings as $warning) {
            echo "   - {$warning}\n";
        }
    } else {
        echo "✅ Cấu hình đã được thiết lập\n";
    }
} else {
    echo "❌ File payment_config.php không tồn tại\n";
}
echo "\n";

// 7. Generate sample crontab
echo "[7/7] Tạo crontab command...\n";
$cronCommand = "*/1 * * * * /usr/bin/php " . __DIR__ . "/cron_check_payment.php >> " . __DIR__ . "/logs/cron.log 2>&1";
$cronFile = __DIR__ . '/crontab_example.txt';
file_put_contents($cronFile, $cronCommand . "\n");
echo "✅ Đã tạo file crontab_example.txt\n";
echo "   Chạy lệnh sau để thêm cronjob:\n";
echo "   \033[1;33mcrontab -e\033[0m\n";
echo "   Sau đó thêm dòng:\n";
echo "   \033[1;32m{$cronCommand}\033[0m\n";
echo "\n";

// Summary
echo "========================================\n";
echo "           HOÀN THÀNH CÀI ĐẶT           \n";
echo "========================================\n\n";

echo "Các bước tiếp theo:\n\n";

echo "1. Cấu hình API ngân hàng:\n";
echo "   - Mở file payment_config.php\n";
echo "   - Điền thông tin đăng nhập ngân hàng\n";
echo "   - Đổi WEBHOOK_SECRET và PAYMENT_API_SECRET\n\n";

echo "2. Cập nhật database schema:\n";
echo "   \033[1;33mmysql -u username -p database_name < db_schema.sql\033[0m\n\n";

echo "3. Thêm cronjob:\n";
echo "   \033[1;33mcrontab -e\033[0m\n";
echo "   Thêm dòng từ file crontab_example.txt\n\n";

echo "4. Test hệ thống:\n";
echo "   \033[1;33mphp cron_check_payment.php\033[0m\n\n";

echo "5. Xem log:\n";
echo "   \033[1;33mtail -f logs/payment.log\033[0m\n";
echo "   \033[1;33mtail -f logs/cron.log\033[0m\n\n";

echo "6. Đọc hướng dẫn chi tiết:\n";
echo "   \033[1;33mcat README_PAYMENT_API.md\033[0m\n\n";

echo "========================================\n";
echo "✅ Setup hoàn tất!\n";
echo "========================================\n";

?>
