<?php
/**
 * File cấu hình mẫu - Copy thành config_payment.php và điền thông tin thực
 */

// Secret key để xác thực webhook (tạo random string mạnh)
define('WEBHOOK_SECRET_KEY', 'CHANGE-THIS-TO-RANDOM-STRING-IN-PRODUCTION');

// Danh sách IP được phép gọi webhook
// Lấy IP từ service provider (Casso, VietQR, etc.)
define('ALLOWED_IPS', [
    // '103.123.456.789', // IP của Casso
    // '103.98.76.54',    // IP của VietQR
    // '127.0.0.1',       // Localhost cho test
]);

// Bật kiểm tra IP (false khi test, true khi production)
define('CHECK_IP_WHITELIST', false);

// File log
define('WEBHOOK_LOG_FILE', __DIR__ . '/logs/payment_webhook.log');

// Chế độ debug (true = log chi tiết, false = chỉ log quan trọng)
define('WEBHOOK_DEBUG', true);

return [
    'secret_key' => WEBHOOK_SECRET_KEY,
    'allowed_ips' => ALLOWED_IPS,
    'check_ip' => CHECK_IP_WHITELIST,
    'log_file' => WEBHOOK_LOG_FILE,
    'debug' => WEBHOOK_DEBUG,
];
