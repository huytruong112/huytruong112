<?php
/**
 * Cấu hình API Thanh Toán Tự Động
 * 
 * Hỗ trợ nhiều dịch vụ thanh toán:
 * - Casso.vn (Đồng bộ giao dịch ngân hàng)
 * - Payos.vn
 * - Các ngân hàng hỗ trợ webhook
 */

// Cấu hình chung
define('PAYMENT_ENABLED', true); // Bật/tắt thanh toán tự động
define('PAYMENT_DEBUG', true); // Chế độ debug (log chi tiết)

// Secret key để xác thực webhook (đổi key này thành key bí mật của bạn)
define('WEBHOOK_SECRET', 'your-secret-key-change-this-' . md5('vpn-vietnam'));

// ===== CẤU HÌNH CASSO.VN =====
// Đăng ký tài khoản tại: https://casso.vn
define('CASSO_ENABLED', true);
define('CASSO_API_KEY', 'YOUR_CASSO_API_KEY_HERE'); // Lấy từ casso.vn
define('CASSO_SECURE_TOKEN', 'YOUR_CASSO_SECURE_TOKEN'); // Token bảo mật webhook

// ===== CẤU HÌNH PAYOS.VN =====
define('PAYOS_ENABLED', false);
define('PAYOS_API_KEY', 'YOUR_PAYOS_API_KEY');
define('PAYOS_CLIENT_ID', 'YOUR_PAYOS_CLIENT_ID');
define('PAYOS_CHECKSUM_KEY', 'YOUR_PAYOS_CHECKSUM_KEY');

// ===== CẤU HÌNH NGÂN HÀNG TRỰC TIẾP =====
// Một số ngân hàng cho phép webhook trực tiếp (cần đăng ký doanh nghiệp)
define('BANK_WEBHOOK_ENABLED', false);
define('BANK_API_KEY', '');

// ===== CÀI ĐẶT GIAO DỊCH =====
define('MIN_TRANSACTION_AMOUNT', 10000); // Số tiền tối thiểu
define('MAX_TRANSACTION_AMOUNT', 50000000); // Số tiền tối đa
define('TRANSACTION_TIMEOUT', 86400); // Timeout giao dịch (24h = 86400s)

// ===== CÀI ĐẶT LOG =====
define('LOG_ENABLED', true);
define('LOG_FILE', __DIR__ . '/logs/payment_webhook.log');
define('LOG_MAX_SIZE', 10485760); // 10MB

// ===== DANH SÁCH IP CHO PHÉP (Whitelist) =====
// Chỉ cho phép các IP này gọi webhook (tăng bảo mật)
// Để trống [] để cho phép tất cả IP (không khuyến khích)
define('ALLOWED_IPS', [
    // IP của Casso.vn
    '103.146.23.96',
    '103.146.23.97',
    '103.146.23.98',
    // IP của server bạn (để test local)
    '127.0.0.1',
    '::1',
    // Thêm các IP khác nếu cần
]);

// ===== THÔNG BÁO =====
define('NOTIFY_ADMIN_ON_SUCCESS', true); // Gửi thông báo cho admin khi thanh toán thành công
define('NOTIFY_USER_ON_SUCCESS', true); // Gửi thông báo cho user
define('ADMIN_EMAIL', 'admin@vpnvietnam.com');
define('ADMIN_TELEGRAM', ''); // Telegram chat ID (nếu có)

/**
 * Hàm log thanh toán
 */
function paymentLog($message, $level = 'INFO') {
    if (!LOG_ENABLED) return;
    
    $logDir = dirname(LOG_FILE);
    if (!file_exists($logDir)) {
        mkdir($logDir, 0755, true);
    }
    
    // Rotate log nếu quá lớn
    if (file_exists(LOG_FILE) && filesize(LOG_FILE) > LOG_MAX_SIZE) {
        rename(LOG_FILE, LOG_FILE . '.' . date('YmdHis') . '.old');
    }
    
    $timestamp = date('Y-m-d H:i:s');
    $logMessage = "[{$timestamp}] [{$level}] {$message}\n";
    file_put_contents(LOG_FILE, $logMessage, FILE_APPEND);
}

/**
 * Kiểm tra IP có được phép không
 */
function isAllowedIP($ip) {
    if (empty(ALLOWED_IPS)) return true; // Cho phép tất cả nếu không config
    return in_array($ip, ALLOWED_IPS);
}

/**
 * Lấy IP của client
 */
function getClientIP() {
    $ip = '';
    if (isset($_SERVER['HTTP_CF_CONNECTING_IP'])) {
        // Cloudflare
        $ip = $_SERVER['HTTP_CF_CONNECTING_IP'];
    } elseif (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ip = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR'])[0];
    } elseif (isset($_SERVER['HTTP_X_REAL_IP'])) {
        $ip = $_SERVER['HTTP_X_REAL_IP'];
    } else {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '';
    }
    return trim($ip);
}

/**
 * Gửi response JSON
 */
function sendJSONResponse($data, $httpCode = 200) {
    http_response_code($httpCode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}
