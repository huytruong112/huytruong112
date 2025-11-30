<?php
/**
 * QR Code Proxy - Ẩn thông tin ngân hàng trong URL
 * SECURE+: File này giúp ẩn thông tin nhạy cảm khỏi view-source
 */
session_start();
require 'config.php';

header('Content-Type: image/png');
header('Cache-Control: no-store, private, max-age=0');
header('Pragma: no-cache');
header('X-Content-Type-Options: nosniff');

// Lấy tham số
$code = $_GET['code'] ?? '';
$sig  = $_GET['sig']  ?? '';

if (empty($code)) {
    http_response_code(400);
    exit;
}

// SECURE+: Verify HMAC signature
$uid = (int)($_SESSION['user_id'] ?? 0);
$payload = 'qr|' . $code . '|' . $uid;
$expectedSig = hash_hmac('sha256', $payload, APP_SECRET ?? 'change-this-secret-32bytes-min');

if (!hash_equals($expectedSig, $sig)) {
    http_response_code(403);
    exit;
}

// Rate limiting
if (!isset($_SESSION['rl'])) $_SESSION['rl'] = [];
if (!isset($_SESSION['rl']['qr_' . $code])) $_SESSION['rl']['qr_' . $code] = [];
$now = time();
$_SESSION['rl']['qr_' . $code] = array_filter($_SESSION['rl']['qr_' . $code], fn($t) => $t > ($now - 60));
if (count($_SESSION['rl']['qr_' . $code]) >= 10) {
    http_response_code(429);
    exit;
}
$_SESSION['rl']['qr_' . $code][] = $now;

// Lấy thông tin giao dịch
try {
    if (!empty($_SESSION['user_id'])) {
        $stmt = $pdo->prepare("
            SELECT t.*, u.username 
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.unique_code = :code AND t.user_id = :uid
            LIMIT 1
        ");
        $stmt->execute([':code' => $code, ':uid' => (int)$_SESSION['user_id']]);
    } else {
        $stmt = $pdo->prepare("
            SELECT t.*, u.username 
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.unique_code = :code
            LIMIT 1
        ");
        $stmt->execute([':code' => $code]);
    }
    
    $tx = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$tx) {
        http_response_code(404);
        exit;
    }

    // Lấy thông tin ngân hàng
    $bankStmt = $pdo->query("SELECT bank_name, account_number, account_holder FROM receiving_accounts ORDER BY id DESC LIMIT 1");
    $bank = $bankStmt ? $bankStmt->fetch(PDO::FETCH_ASSOC) : null;
    
    if (!$bank) {
        http_response_code(404);
        exit;
    }

    // Tạo URL QR từ VietQR
    $bank_code = strtolower($bank['bank_name']);
    $amount = (int)$tx['amount_paid'];
    $qr_url = "https://img.vietqr.io/image/" . $bank_code . "-" . 
              $bank['account_number'] . "-compact2.png?amount={$amount}&addInfo=" . 
              urlencode($tx['unique_code']) . "&accountName=" . 
              urlencode($bank['account_holder'] ?? '');

    // Fetch QR image và trả về
    $context = stream_context_create([
        'http' => [
            'timeout' => 10,
            'user_agent' => 'Mozilla/5.0',
        ],
        'ssl' => [
            'verify_peer' => true,
            'verify_peer_name' => true,
        ]
    ]);
    
    $imageData = @file_get_contents($qr_url, false, $context);
    
    if ($imageData === false) {
        http_response_code(502);
        exit;
    }

    // Cache trong session để giảm requests
    $_SESSION['qr_cache_' . $code] = [
        'data' => base64_encode($imageData),
        'time' => time()
    ];

    echo $imageData;
    exit;

} catch (Throwable $e) {
    error_log('[QR PROXY] ' . $e->getMessage());
    http_response_code(500);
    exit;
}
