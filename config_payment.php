<?php
/**
 * Cấu hình API thanh toán tự động
 * File này chứa các thông tin cấu hình cho các API ngân hàng và cổng thanh toán
 */

// Cấu hình bảo mật cho API
define('API_SECRET_KEY', 'your-secret-key-here-change-this'); // Thay đổi key này để bảo mật
define('WEBHOOK_TOKEN', 'your-webhook-token-here-change-this'); // Token để xác thực webhook

// Cấu hình cho VietQR API (nếu sử dụng)
define('VIETQR_API_URL', 'https://api.vietqr.io/v2/transactions');
define('VIETQR_API_KEY', ''); // API key của VietQR (nếu có)

// Cấu hình cho ngân hàng API (MB Bank, VCB, etc.)
$bank_api_config = [
    'enabled' => true,
    'bank_type' => 'mbbank', // mbbank, vcb, acb, techcombank, etc.
    'api_url' => '',
    'username' => '',
    'password' => '',
    'account_number' => '',
];

// Cấu hình cho cổng thanh toán VNPay (nếu sử dụng)
$vnpay_config = [
    'enabled' => false,
    'vnp_TmnCode' => '', // Mã website tại VNPay
    'vnp_HashSecret' => '', // Chuỗi bí mật
    'vnp_Url' => 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
    'vnp_ReturnUrl' => '', // URL return sau khi thanh toán
];

// Cấu hình cho Momo (nếu sử dụng)
$momo_config = [
    'enabled' => false,
    'partner_code' => '',
    'access_key' => '',
    'secret_key' => '',
    'api_endpoint' => 'https://test-payment.momo.vn/v2/gateway/api/create',
];

// Cấu hình tự động kiểm tra giao dịch
define('AUTO_CHECK_ENABLED', true); // Bật/tắt tự động kiểm tra
define('CHECK_INTERVAL', 60); // Kiểm tra mỗi 60 giây
define('TRANSACTION_TIMEOUT', 86400); // Thời gian timeout giao dịch: 24 giờ (86400 giây)

// Cấu hình log
define('LOG_PAYMENT_ENABLED', true);
define('LOG_FILE_PATH', __DIR__ . '/logs/payment.log');

// Cấu hình email thông báo (tùy chọn)
define('EMAIL_NOTIFICATION_ENABLED', false);
define('ADMIN_EMAIL', 'admin@example.com');

// Danh sách IP được phép gọi webhook (để bảo mật)
$allowed_webhook_ips = [
    '127.0.0.1',
    '::1',
    // Thêm IP của ngân hàng/cổng thanh toán vào đây
];

return [
    'bank_api_config' => $bank_api_config,
    'vnpay_config' => $vnpay_config,
    'momo_config' => $momo_config,
    'allowed_webhook_ips' => $allowed_webhook_ips,
];
