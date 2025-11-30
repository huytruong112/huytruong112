#!/usr/bin/env php
<?php
/**
 * Cron Job - Kiểm tra thanh toán định kỳ
 * 
 * Thêm vào crontab:
 * */1 * * * * /usr/bin/php /path/to/cron_check_payment.php >> /path/to/logs/cron.log 2>&1
 * 
 * Chạy mỗi phút một lần
 */

// Đảm bảo chỉ chạy từ CLI
if (php_sapi_name() !== 'cli') {
    die('This script must be run from command line');
}

require_once __DIR__ . '/db.php';
require_once __DIR__ . '/auto_payment_check.php';
require_once __DIR__ . '/payment_config.php';

// Thiết lập múi giờ
date_default_timezone_set('Asia/Ho_Chi_Minh');

// Log file
$logFile = __DIR__ . '/logs/cron.log';
$logDir = dirname($logFile);
if (!file_exists($logDir)) {
    mkdir($logDir, 0755, true);
}

function logCron($message) {
    global $logFile;
    $timestamp = date('Y-m-d H:i:s');
    $logMessage = "[{$timestamp}] [CRON] {$message}\n";
    file_put_contents($logFile, $logMessage, FILE_APPEND);
    echo $logMessage; // Also output to console
}

// Kiểm tra lock file để tránh chạy đồng thời
$lockFile = __DIR__ . '/logs/payment_cron.lock';
if (file_exists($lockFile)) {
    $lockTime = filemtime($lockFile);
    // Nếu lock file quá 5 phút thì xóa (process bị treo)
    if (time() - $lockTime > 300) {
        unlink($lockFile);
        logCron("Xóa lock file cũ (quá 5 phút)");
    } else {
        logCron("Cronjob đang chạy (lock file exists), bỏ qua lần này");
        exit(0);
    }
}

// Tạo lock file
file_put_contents($lockFile, getmypid());

try {
    logCron("===== BẮT ĐẦU CRON JOB KIỂM TRA THANH TOÁN =====");
    
    // Kiểm tra config
    if (!PAYMENT_AUTO_CHECK_ENABLED) {
        logCron("Auto check bị tắt trong config");
        unlink($lockFile);
        exit(0);
    }

    // Chạy processor
    $processor = new AutoPaymentProcessor($conn);
    $processor->process();

    logCron("===== KẾT THÚC CRON JOB =====");

} catch (Exception $e) {
    logCron("LỖI: " . $e->getMessage());
    logCron("Stack trace: " . $e->getTraceAsString());
} finally {
    // Xóa lock file
    if (file_exists($lockFile)) {
        unlink($lockFile);
    }
}

?>
