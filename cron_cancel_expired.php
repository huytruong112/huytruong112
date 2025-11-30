<?php
/**
 * Cron Job - Tự động hủy giao dịch quá hạn
 * 
 * Chạy script này mỗi giờ để hủy các giao dịch pending quá 24h
 * 
 * Cách thiết lập cron:
 * crontab -e
 * 
 * Thêm dòng:
 * 0 * * * * /usr/bin/php /path/to/cron_cancel_expired.php >> /path/to/logs/cron.log 2>&1
 * 
 * (Chạy mỗi giờ vào phút 0)
 */

date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once __DIR__ . '/db.php';

echo "[" . date('Y-m-d H:i:s') . "] Starting cron job: Cancel expired transactions\n";

try {
    // Hủy các giao dịch pending quá 24h
    $sql = "UPDATE transactions 
            SET status = 'cancelled', 
                updated_at = NOW()
            WHERE status = 'pending' 
            AND TIMESTAMPDIFF(SECOND, transaction_date, NOW()) > 86400";
    
    $result = $conn->query($sql);
    $affectedRows = $conn->affected_rows;
    
    echo "[" . date('Y-m-d H:i:s') . "] Cancelled {$affectedRows} expired transaction(s)\n";
    
    // Log vào database (nếu có bảng cron_logs)
    if ($affectedRows > 0) {
        $logSql = "INSERT INTO cron_logs (cron_name, message, created_at) 
                   VALUES ('cancel_expired_transactions', 'Cancelled {$affectedRows} transaction(s)', NOW())";
        $conn->query($logSql);
    }
    
    echo "[" . date('Y-m-d H:i:s') . "] Cron job completed successfully\n";
    
} catch (Exception $e) {
    echo "[" . date('Y-m-d H:i:s') . "] ERROR: " . $e->getMessage() . "\n";
    exit(1);
}

exit(0);
