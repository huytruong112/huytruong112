<?php
session_start();
require 'config.php'; // PDO: $pdo

/* ================= SECURE+: Security headers & helpers ================= */
header('Cache-Control: no-store, private, max-age=0');             // SECURE+
header('Pragma: no-cache');                                        // SECURE+
header('X-Frame-Options: DENY');                                   // SECURE+
header('X-Content-Type-Options: nosniff');                         // SECURE+
header('Referrer-Policy: no-referrer');                            // SECURE+
header("Content-Security-Policy: default-src 'self'; img-src 'self' https://img.vietqr.io data:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; frame-ancestors 'none'"); // SECURE+

ini_set('display_errors','0');                                      // SECURE+
ini_set('log_errors','1');                                          // SECURE+

if (!defined('APP_SECRET')) {                                       // SECURE+
    // Nếu đã có APP_SECRET trong config.php/.env thì giữ; nếu chưa có thì fallback tạm.
    define('APP_SECRET', 'change-this-secret-32bytes-min');         // SECURE+
}
function hmac_sign(string $payload): string {                        // SECURE+
    return hash_hmac('sha256', $payload, APP_SECRET);
}
function hmac_verify(string $payload, ?string $sig): bool {          // SECURE+
    return is_string($sig) && hash_equals(hmac_sign($payload), $sig);
}
function rate_limited(string $key, int $max, int $window): bool {    // SECURE+
    $now = time();
    if (!isset($_SESSION['rl'][$key])) $_SESSION['rl'][$key] = [];
    $_SESSION['rl'][$key] = array_filter($_SESSION['rl'][$key], fn($t)=>$t > ($now-$window));
    if (count($_SESSION['rl'][$key]) >= $max) return true;
    $_SESSION['rl'][$key][] = $now;
    return false;
}

/* ================= SMTP config ================= */
if (!defined('SMTP_HOST')) define('SMTP_HOST', 'pro211.emailserver.vn');
if (!defined('SMTP_USER')) define('SMTP_USER', 'support.vpn@vpnvietnam.com');
if (!defined('SMTP_PASS')) define('SMTP_PASS', 'Vpnvietnam123@!');
if (!defined('SMTP_PORT')) define('SMTP_PORT', 587);

/* ================= PHPMailer bootstrap (an toàn) ================= */
$haveMailer = false;
try {
    $autoload = __DIR__ . '/vendor/autoload.php';
    if (is_file($autoload)) {
        require_once $autoload; // Composer
        $haveMailer = true;
    } else {
        $p1 = __DIR__ . '/PHPMailer/src/PHPMailer.php';
        $p2 = __DIR__ . '/PHPMailer/src/SMTP.php';
        $p3 = __DIR__ . '/PHPMailer/src/Exception.php';
        if (is_file($p1) && is_file($p2) && is_file($p3)) {
            require_once $p1; require_once $p2; require_once $p3;
            $haveMailer = true;
        }
    }
} catch (Throwable $e) {
    error_log('[PAY PAGE][PHPMailer bootstrap] ' . $e->getMessage());
    $haveMailer = false;
}
if ($haveMailer) { class_exists('PHPMailer\PHPMailer\PHPMailer'); }
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

/* ================= Helpers ================= */
function h($v){ return htmlspecialchars((string)($v ?? ''), ENT_QUOTES, 'UTF-8'); }

/* ---------- Email templates: PENDING ---------- */
function build_deposit_email_html(array $tx, array $bank): string {
    $username = h($tx['username'] ?? 'Khách hàng');
    $email    = h($tx['email'] ?? '');
    $code     = h($tx['unique_code'] ?? '');
    $amount   = number_format((int)($tx['amount_paid'] ?? 0), 0, ',', '.');

    $bankName = h($bank['bank_name'] ?? '');
    $account  = h($bank['account_number'] ?? '');
    $holder   = h($bank['account_holder'] ?? '');
    $branch   = h($bank['branch'] ?? '');

    $manageUrl  = 'https://user.vpnvietnam.com/pay.php?code=' . urlencode($tx['unique_code'] ?? '');
    $supportUrl = 'https://user.vpnvietnam.com/support.php';

    // VietQR (nếu đủ thông tin)
    $qrTag = '';
    if (!empty($bank['account_number']) && !empty($bank['bank_name'])) {
        $bank_code = strtolower($bank['bank_name']);
        $amountInt = (int)($tx['amount_paid'] ?? 0);
        $qr_url = "https://img.vietqr.io/image/" . $bank_code . "-" . $bank['account_number'] . "-compact2.png?amount={$amountInt}&addInfo=" . urlencode($tx['unique_code'] ?? '') . "&accountName=" . urlencode($bank['account_holder'] ?? '');
        $qrTag = '<p class="fw-semibold">Quét QR để chuyển khoản nhanh:</p><img referrerpolicy="no-referrer" src="'.h($qr_url).'" alt="QR Banking" style="max-width:260px;border:1px solid #ddd;border-radius:8px;padding:5px;background:#fff">'; // SECURE+
    }

    return <<<HTML
<!DOCTYPE html>
<html lang="vi">
  <body style="font-family:Arial,Helvetica,sans-serif;line-height:1.6;color:#222">
    <div style="max-width:680px;margin:auto;border:1px solid #eee;border-radius:12px;padding:24px">
      <div style="text-align:center;margin-bottom:12px">
        <img src="https://vpnvietnam.com/images/logojk.png" alt="VPN Viet Nam" style="height:52px">
      </div>
      <h2 style="margin:8px 0 0;">Tạo lệnh nạp tiền thành công</h2>
      <p>Chào <b>{$username}</b>, chúng tôi đã ghi nhận yêu cầu nạp tiền của bạn.</p>

      <table cellpadding="8" cellspacing="0" style="width:100%;border:1px solid #eee;border-radius:8px">
        <tr><td><b>Khách hàng</b></td><td>{$username}</td></tr>
        <tr><td><b>Email</b></td><td>{$email}</td></tr>
        <tr><td><b>Mã giao dịch</b></td><td><code>{$code}</code></td></tr>
        <tr><td><b>Số tiền</b></td><td><b>{$amount} VND</b></td></tr>
        <tr><td><b>Trạng thái</b></td><td>pending (Chờ thanh toán)</td></tr>
      </table>

      <h3 style="margin-top:18px">Thông tin chuyển khoản</h3>
      <ul>
        <li><b>Ngân hàng</b>: {$bankName}</li>
        <li><b>Số tài khoản</b>: {$account}</li>
        <li><b>Chủ tài khoản</b>: {$holder}</li>
        <li><b>Chi nhánh</b>: {$branch}</li>
        <li><b>Nội dung chuyển khoản</b>: <code style="padding:1px 6px;border:1px solid #ddd;border-radius:6px;background:#fafafa">{$code}</code></li>
      </ul>

      {$qrTag}

      <p style="color:#cc0000"><b>Lưu ý:</b> Vui lòng ghi <b>đúng nội dung chuyển khoản</b> để hệ thống khớp lệnh nhanh. Lệnh sẽ tự huỷ sau <b>24 giờ</b> nếu chưa thanh toán.</p>

      <h3>Phương thức USDT (tuỳ chọn)</h3>
      <p>Địa chỉ USDT TRC20: <code style="padding:1px 6px;border:1px solid #ddd;border-radius:6px;background:#fafafa">TUmGMxEAF5hP1P9c1Tf24yg5cwxfo7GW3m</code><br/>
      Tỷ giá mặc định: <b>25.700</b> VND/USDT. Sau khi chuyển, vui lòng báo xác nhận tại <a href="{$supportUrl}">Trung tâm hỗ trợ</a>.</p>

      <p>Bạn có thể mở lại hướng dẫn thanh toán: <a href="{$manageUrl}">{$manageUrl}</a></p>

      <h3>Hỗ trợ 24/7</h3>
      <ul>
        <li>📧 Email: <a href="mailto:support.vpn@vpnvietnam.com">support.vpn@vpnvietnam.com</a></li>
        <li>📞 Hotline/Zalo: 0826.003.926</li>
        <li>🌐 Website: <a href="https://vpnvietnam.com">vpnvietnam.com</a></li>
      </ul>

      <p style="margin-top:24px">Trân trọng,<br><b>Đội ngũ VPN Việt Nam</b></p>
      <hr style="border:none;border-top:1px solid #eee;margin:16px 0">
      <p style="font-size:12px;color:#666">Bạn nhận được email này vì đã tạo lệnh nạp tiền trên hệ thống VPN Việt Nam.</p>
    </div>
  </body>
</html>
HTML;
}
function build_deposit_email_text(array $tx, array $bank): string {
    $username = (string)($tx['username'] ?? 'Khach hang');
    $code     = (string)($tx['unique_code'] ?? '');
    $amount   = number_format((int)($tx['amount_paid'] ?? 0), 0, ',', '.');

    $bankName = (string)($bank['bank_name'] ?? '');
    $account  = (string)($bank['account_number'] ?? '');
    $holder   = (string)($bank['account_holder'] ?? '');
    $branch   = (string)($bank['branch'] ?? '');

    $manageUrl  = 'https://user.vpnvietnam.com/pay.php?code=' . ($tx['unique_code'] ?? '');
    $supportUrl = 'https://user.vpnvietnam.com/support.php';

    return
"Chao {$username},

Lenh nap tien da duoc tao (pending).
Ma giao dich: {$code}
So tien: {$amount} VND

Thong tin chuyen khoan:
- Ngan hang: {$bankName}
- So tai khoan: {$account}
- Chu tai khoan: {$holder}
- Chi nhanh: {$branch}
- Noi dung CK: {$code}

Quet QR (neu co tren giao dien) de chuyen nhanh.
Luu y: Ghi dung noi dung CK de khop lenh nhanh. Lenh tu huy sau 24 gio neu chua thanh toan.

USDT (tuy chon):
- Dia chi TRC20: TUmGMxEAF5hP1P9c1Tf24yg5cwxfo7GW3m
- Ty gia mac dinh: 25.700 VND/USDT
- Xac nhan: {$supportUrl}

Mo lai huong dan thanh toan: {$manageUrl}

Ho tro 24/7:
- Email: support.vpn@vpnvietnam.com
- Hotline/Zalo: 0826.003.926
- Website: vpnvietnam.com

Tran trong,
VPN Viet Nam";
}

/* ---------- Email templates: SUCCESS ---------- */
function build_success_email_html(array $tx, float $newBalance, array $bank): string {
    $username = h($tx['username'] ?? 'Khách hàng');
    $code     = h($tx['unique_code'] ?? '');
    $amount   = number_format((int)($tx['amount_paid'] ?? 0), 0, ',', '.');
    $date     = h(date('d/m/Y H:i', strtotime($tx['transaction_date'] ?? 'now')));
    $bal      = number_format($newBalance, 0, ',', '.');

    return <<<HTML
<!DOCTYPE html>
<html lang="vi">
  <body style="font-family:Arial,Helvetica,sans-serif;line-height:1.6;color:#222">
    <div style="max-width:680px;margin:auto;border:1px solid #eee;border-radius:12px;padding:24px">
      <div style="text-align:center;margin-bottom:12px">
        <img src="https://vpnvietnam.com/images/logojk.png" alt="VPN Viet Nam" style="height:52px">
      </div>
      <h2>Xác nhận nạp tiền thành công</h2>
      <p>Chào <b>{$username}</b>, lệnh nạp tiền của bạn đã được <b>xác nhận</b>. Thông tin biên nhận:</p>
      <table cellpadding="8" cellspacing="0" style="width:100%;border:1px solid #eee;border-radius:8px">
        <tr><td><b>Mã giao dịch</b></td><td><code>{$code}</code></td></tr>
        <tr><td><b>Số tiền</b></td><td><b>{$amount} VND</b></td></tr>
        <tr><td><b>Ngày tạo lệnh</b></td><td>{$date}</td></tr>
        <tr><td><b>Trạng thái</b></td><td>Thành công</td></tr>
        <tr><td><b>Số dư mới</b></td><td><b>{$bal} VND</b></td></tr>
      </table>
      <p>Bạn có thể xem số dư & lịch sử tại: <a href="https://user.vpnvietnam.com/dashboard.php">Dashboard</a> · <a href="https://user.vpnvietnam.com/deposit.php">Lịch sử nạp tiền</a></p>
      <h3>Hỗ trợ 24/7</h3>
      <ul>
        <li>📧 support.vpn@vpnvietnam.com</li>
        <li>📞 0826.003.926</li>
        <li>🌐 vpnvietnam.com</li>
      </ul>
    </div>
  </body>
</html>
HTML;
}
function build_success_email_text(array $tx, float $newBalance): string {
    $username = (string)($tx['username'] ?? 'Khach hang');
    $code     = (string)($tx['unique_code'] ?? '');
    $amount   = number_format((int)($tx['amount_paid'] ?? 0), 0, ',', '.');
    $date     = date('d/m/Y H:i', strtotime($tx['transaction_date'] ?? 'now'));
    $bal      = number_format($newBalance, 0, ',', '.');

    return
"Chao {$username},

Lenh nap tien da duoc XAC NHAN.
- Ma giao dich: {$code}
- So tien: {$amount} VND
- Ngay tao lenh: {$date}
- Trang thai: Thanh cong
- So du moi: {$bal} VND

Xem so du & lich su: Dashboard / Lich su nap tien.
Ho tro: support.vpn@vpnvietnam.com - 0826.003.926";
}

/* ---------- Senders ---------- */
function send_deposit_email_pending(array $tx, array $bank): bool {
    if (!class_exists('\PHPMailer\PHPMailer\PHPMailer') || empty($tx['email'])) return false;
    try {
        $mail = new PHPMailer(true);
        $mail->isSMTP();
        $mail->Host       = SMTP_HOST;
        $mail->SMTPAuth   = true;
        $mail->Username   = SMTP_USER;
        $mail->Password   = SMTP_PASS;
        $mail->SMTPAutoTLS= true;                                                       // SECURE+
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port       = SMTP_PORT;
        $mail->CharSet    = 'UTF-8';
        $mail->SMTPOptions = ['ssl'=>['verify_peer'=>true,'verify_peer_name'=>true,'allow_self_signed'=>false]]; // SECURE+

        $toEmail = (string)$tx['email'];
        $toName  = (string)($tx['full_name'] ?? $tx['username'] ?? $toEmail);
        $mail->setFrom(SMTP_USER, 'VPN Việt Nam');
        $mail->addAddress($toEmail, $toName);
        $mail->isHTML(true);
        $mail->Subject = 'Hướng dẫn thanh toán lệnh nạp tiền – VPN Việt Nam';
        $mail->Body    = build_deposit_email_html($tx, $bank);
        $mail->AltBody = build_deposit_email_text($tx, $bank);
        $mail->send();
        return true;
    } catch (Throwable $e) { error_log('[PAY PAGE][send_pending_mail] ' . $e->getMessage()); return false; }
}
function send_deposit_email_success(PDO $pdo, array $tx): bool {
    if (!class_exists('\PHPMailer\PHPMailer\PHPMailer')) return false;

    // Lấy số dư mới từ users để đưa vào mail
    $stU = $pdo->prepare("SELECT username, email, full_name, balance FROM users WHERE id = :uid LIMIT 1");
    $stU->execute([':uid' => $tx['user_id']]);
    $user = $stU->fetch(PDO::FETCH_ASSOC);
    if (!$user || empty($user['email'])) return false;

    $newBalance = (float)($user['balance'] ?? 0);

    $bank = $pdo->query("SELECT bank_name, account_number, account_holder, branch FROM receiving_accounts ORDER BY id DESC LIMIT 1");
    $bankInfo = $bank ? $bank->fetch(PDO::FETCH_ASSOC) : [];

    try {
        $mail = new PHPMailer(true);
        $mail->isSMTP();
        $mail->Host       = SMTP_HOST;
        $mail->SMTPAuth   = true;
        $mail->Username   = SMTP_USER;
        $mail->Password   = SMTP_PASS;
        $mail->SMTPAutoTLS= true;                                                       // SECURE+
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port       = SMTP_PORT;
        $mail->CharSet    = 'UTF-8';
        $mail->SMTPOptions = ['ssl'=>['verify_peer'=>true,'verify_peer_name'=>true,'allow_self_signed'=>false]]; // SECURE+

        $toEmail = (string)$user['email'];
        $toName  = (string)($user['full_name'] ?? $user['username'] ?? $toEmail);
        $mail->setFrom(SMTP_USER, 'VPN Việt Nam');
        $mail->addAddress($toEmail, $toName);

        $mail->isHTML(true);
        $mail->Subject = 'Xác nhận nạp tiền thành công – VPN Việt Nam';
        $mail->Body    = build_success_email_html($tx, $newBalance, $bankInfo);
        $mail->AltBody = build_success_email_text($tx, $newBalance);

        $mail->send();

        // Thử đánh dấu email_sent_at (nếu có cột)
        try {
            $pdo->prepare("UPDATE transactions SET email_sent_at = NOW() WHERE transaction_id = :tid")->execute([':tid' => $tx['transaction_id']]);
        } catch (Throwable $e) {}

        return true;
    } catch (Throwable $e) { error_log('[PAY PAGE][send_success_mail] ' . $e->getMessage()); return false; }
}

/* ================= AJAX: gửi email biên nhận khi đã success =================
 * Giữ nguyên route GET, nhưng yêu cầu chữ ký HMAC + rate-limit + (nếu có) owner-check.
 * pay.php?ajax=send_success_email&code=TS12345&sig=...
 */
if (isset($_GET['ajax']) && $_GET['ajax'] === 'send_success_email') {
    header('Content-Type: application/json; charset=utf-8');
    $codeAjax = $_GET['code'] ?? '';
    $sigAjax  = $_GET['sig']  ?? null;                                  // SECURE+

    if ($codeAjax === '') { echo json_encode(['ok'=>false,'error'=>'Missing code']); exit; }

    // Rate limit theo code (5 lần / 10 phút)
    if (rate_limited('sse_'.$codeAjax, 5, 600)) {                        // SECURE+
        http_response_code(429);
        echo json_encode(['ok'=>false,'error'=>'rate_limited']); exit;
    }

    // Nếu có user đăng nhập → ràng buộc owner trong SQL
    if (!empty($_SESSION['user_id'])) {                                  // SECURE+
        $stmt = $pdo->prepare("
            SELECT t.*, u.username, u.email, u.full_name
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.unique_code = :code AND t.user_id = :uid
            LIMIT 1
        ");
        $stmt->execute([':code' => $codeAjax, ':uid' => (int)$_SESSION['user_id']]);
    } else {
        $stmt = $pdo->prepare("
            SELECT t.*, u.username, u.email, u.full_name
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.unique_code = :code
            LIMIT 1
        ");
        $stmt->execute([':code' => $codeAjax]);
    }
    $txAjax = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$txAjax) { echo json_encode(['ok'=>false,'error'=>'Not found']); exit; }

    // Bắt buộc chữ ký HMAC theo (action|code|userId)
    $uid = (int)($_SESSION['user_id'] ?? 0);                              // SECURE+
    $payload = 'send_success_email|'.$codeAjax.'|'.$uid;                  // SECURE+
    if (!hmac_verify($payload, $sigAjax)) {                               // SECURE+
        http_response_code(400);
        echo json_encode(['ok'=>false,'error'=>'bad_sig']); exit;
    }

    // chỉ gửi khi đã success & chưa gửi trước đó (nếu có cột email_sent_at)
    $alreadySent = !empty($txAjax['email_sent_at']);
    if (!in_array($txAjax['status'], ['Thành công','success'], true)) {
        echo json_encode(['ok'=>false,'error'=>'Not success']); exit;
    }
    if ($alreadySent) {
        echo json_encode(['ok'=>true,'email_sent'=>false,'msg'=>'already_sent']); exit;
    }

    $sent = send_deposit_email_success($pdo, $txAjax);
    echo json_encode(['ok'=>true,'email_sent'=>$sent]);
    exit;
}

/* ================= Load transaction ================= */
$transaction_code = $_GET['code'] ?? '';
if ($transaction_code === '') {
    die("Mã giao dịch không hợp lệ!");
}

// Lấy giao dịch theo mã (thêm email/full_name để gửi mail)
// Nếu có user đăng nhập thì ràng buộc owner, còn không thì giữ nguyên hành vi cũ.
if (!empty($_SESSION['user_id'])) {                                       // SECURE+
    $stmt = $pdo->prepare("
        SELECT t.*, u.username, u.email, u.full_name
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        WHERE t.unique_code = :code AND t.user_id = :uid
        LIMIT 1
    ");
    $stmt->execute([':code' => $transaction_code, ':uid' => (int)$_SESSION['user_id']]);
} else {
    $stmt = $pdo->prepare("
        SELECT t.*, u.username, u.email, u.full_name
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        WHERE t.unique_code = :code
        LIMIT 1
    ");
    $stmt->execute([':code' => $transaction_code]);
}
$tx = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$tx) {
    die("Không tìm thấy giao dịch.");
}

// Lấy tài khoản nhận
$bankStmt = $pdo->query("SELECT * FROM receiving_accounts ORDER BY id DESC LIMIT 1");
$bank = $bankStmt ? $bankStmt->fetch(PDO::FETCH_ASSOC) : [];

// QR link
$qr_url = '';
if (!empty($bank['account_number']) && !empty($bank['bank_name'])) {
    $bank_code = strtolower($bank['bank_name']);
    $amount = (int)$tx['amount_paid'];
    $qr_url = "https://img.vietqr.io/image/" . $bank_code . "-" . $bank['account_number'] . "-compact2.png?amount={$amount}&addInfo=" . urlencode($tx['unique_code']) . "&accountName=" . urlencode($bank['account_holder'] ?? '');
}

/* ================= Auto-send pending email (1 lần) + Resend ================= */
$resent = false; $justSentPending = false;
// Thêm HMAC & rate-limit cho resend=1 nhưng vẫn giữ GET để không phá luồng hiện tại
if (isset($_GET['resend']) && $_GET['resend'] === '1' && $tx['status'] === 'pending' && !empty($tx['email'])) {
    // SECURE+: kiểm tra chữ ký & rate-limit
    $sigResend = $_GET['sig'] ?? null;                                     // SECURE+
    $uid = (int)($_SESSION['user_id'] ?? 0);                                // SECURE+
    $payload = 'resend|'.$transaction_code.'|'.$uid;                        // SECURE+
    if (!hmac_verify($payload, $sigResend)) {                               // SECURE+
        http_response_code(400);
        die('Chữ ký không hợp lệ.');                                        // SECURE+
    }
    if (rate_limited('rp_'.$transaction_code, 3, 3600)) {                   // SECURE+
        http_response_code(429);
        die('Thao tác quá nhiều, vui lòng thử lại sau.');                   // SECURE+
    }

    $resent = true;
    $justSentPending = send_deposit_email_pending($tx, $bank);
    $_SESSION['pay_last_pending_sent_'.$transaction_code] = time();
} else {
    if ($tx['status'] === 'pending' && empty($_SESSION['pay_pending_sent_'.$transaction_code]) && !empty($tx['email'])) {
        $justSentPending = send_deposit_email_pending($tx, $bank);
        $_SESSION['pay_pending_sent_'.$transaction_code] = 1;
        $_SESSION['pay_last_pending_sent_'.$transaction_code] = time();
    }
}

// Pre-sign URL-safe signatures cho các hành động GET hiện có
$uid = (int)($_SESSION['user_id'] ?? 0);                                   // SECURE+
$sig_link_resend = hmac_sign('resend|'.$transaction_code.'|'.$uid);        // SECURE+
$sig_link_sse    = hmac_sign('send_success_email|'.$transaction_code.'|'.$uid); // SECURE+

// Mã hóa thông tin nhạy cảm để ẩn khi view-source
$sensitive_data = [
    'bank_name' => $bank['bank_name'] ?? '',
    'account_number' => $bank['account_number'] ?? '',
    'account_holder' => $bank['account_holder'] ?? '',
    'branch' => $bank['branch'] ?? '',
    'qr_url' => $qr_url,
    'unique_code' => $tx['unique_code'],
    'status' => $tx['status']
];
$encoded_data = base64_encode(json_encode($sensitive_data));
?>
<!DOCTYPE html>
<html lang="vi" data-bs-theme="auto">
<head>
  <meta charset="UTF-8">
  <title>Thanh Toán - <?= h($transaction_code) ?></title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive"><!-- SECURE+ -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  
  <!-- SECURITY: Anti-inspection & source protection -->
  <script>
    // Detect DevTools and redirect
    (function(){var _0x5a2b=['devtools','open','location','href','about:blank'];(function(){const _0x3e4f=window.outerWidth-window.innerWidth>160||window.outerHeight-window.innerHeight>160;if(_0x3e4f){window[_0x5a2b[2]][_0x5a2b[3]]=_0x5a2b[4];}})();setInterval(function(){const _0x3e4f=window.outerWidth-window.innerWidth>160||window.outerHeight-window.innerHeight>160;if(_0x3e4f){window[_0x5a2b[2]][_0x5a2b[3]]=_0x5a2b[4];}},1000);})();
    
    // Clear console continuously
    setInterval(function(){console.clear();},100);
    
    // Override console methods
    (function(){const _0xc=['log','warn','error','info','debug','table','trace'];_0xc.forEach(m=>{console[m]=function(){}});})();
    
    // Disable right-click
    document.addEventListener('contextmenu',e=>e.preventDefault());
    
    // Disable key shortcuts (F12, Ctrl+Shift+I/J/C, Ctrl+U, Ctrl+S)
    document.addEventListener('keydown',function(e){if(e.keyCode==123||e.ctrlKey&&e.shiftKey&&[73,74,67].includes(e.keyCode)||e.ctrlKey&&[85,83].includes(e.keyCode)){e.preventDefault();return false;}});
    
    // Disable text selection and copy
    document.addEventListener('selectstart',e=>e.preventDefault());
    document.addEventListener('copy',e=>e.preventDefault());
    
    // Detect and prevent inspect element
    document.addEventListener('mousedown',function(e){if(e.button==2){e.preventDefault();return false;}});
    
    // Anti-debugger technique
    (function(){function _0xdbg(){debugger;}setInterval(_0xdbg,100);})();
  </script>
  
  <!-- Hidden encoded data -->
  <script id="secure-data" type="application/x-custom-data" style="display:none !important;">/*<?= $encoded_data ?>*/</script>
  
  <!-- Main functionality (obfuscated) -->
  <script>
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-bs-theme', 'dark');
    }

    const _0x4d2a=['check_transaction_status.php?code=<?= urlencode($transaction_code) ?>','json','status','Thành công','success','pay.php?ajax=send_success_email&code=<?= urlencode($transaction_code) ?>&sig=<?= urlencode($sig_link_sse) ?>','dashboard.php','href','location'];
    function checkTransactionStatus(){fetch(_0x4d2a[0]).then(r=>r[_0x4d2a[1]]()).then(d=>{if(!d)return;if(d[_0x4d2a[2]]===_0x4d2a[3]||d[_0x4d2a[2]]===_0x4d2a[4]){fetch(_0x4d2a[5]).then(r=>r[_0x4d2a[1]]()).then(_=>{window[_0x4d2a[8]][_0x4d2a[7]]=_0x4d2a[6];}).catch(_=>{window[_0x4d2a[8]][_0x4d2a[7]]=_0x4d2a[6];});}});}
    setInterval(checkTransactionStatus,5000);
    
    // Decode và hiển thị thông tin nhạy cảm
    document.addEventListener('DOMContentLoaded',function(){
      try{
        const _0xsd=document.getElementById('secure-data');
        if(!_0xsd)return;
        const _0xtxt=_0xsd.textContent.replace(/\/\*|\*\//g,'');
        const _0xdata=JSON.parse(atob(_0xtxt));
        const _0xbank=document.getElementById('bank-info-container');
        const _0xqr=document.getElementById('qr-container');
        
        // Check status - chỉ hiển thị nếu không phải "Đã hủy"
        if(_0xdata.status==='Đã hủy'||_0xdata.status==='cancelled'){
          if(_0xbank)_0xbank.style.display='none';
          return;
        }
        
        if(_0xbank&&_0xdata.bank_name){
          let _0xhtml='<h5 class="text-primary mb-3">🏦 Thông tin chuyển khoản:</h5><ul class="list-unstyled">';
          _0xhtml+='<li><strong>Ngân hàng:</strong> '+_0xe(_0xdata.bank_name)+'</li>';
          _0xhtml+='<li><strong>Số tài khoản:</strong> '+_0xe(_0xdata.account_number)+'</li>';
          _0xhtml+='<li><strong>Chủ tài khoản:</strong> '+_0xe(_0xdata.account_holder)+'</li>';
          if(_0xdata.branch)_0xhtml+='<li><strong>Chi nhánh:</strong> '+_0xe(_0xdata.branch)+'</li>';
          _0xhtml+='<li><strong>Nội dung chuyển khoản:</strong> <span class="fw-bold text-danger">'+_0xe(_0xdata.unique_code)+'</span></li>';
          _0xhtml+='</ul>';
          _0xbank.innerHTML=_0xhtml;
        }
        
        if(_0xqr&&_0xdata.qr_url){
          let _0xqrhtml='<div class="text-center qr-box mt-4 mb-3">';
          _0xqrhtml+='<p class="fw-semibold">📱 Quét mã QR để chuyển khoản nhanh:</p>';
          _0xqrhtml+='<img referrerpolicy="no-referrer" src="'+_0xe(_0xdata.qr_url)+'" alt="QR Banking" class="img-fluid" style="max-width:280px;">';
          _0xqrhtml+='</div>';
          _0xqr.innerHTML=_0xqrhtml;
        }
        
        _0xsd.remove();
      }catch(e){}
    });
    
    function _0xe(t){
      const m={'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'};
      return String(t||'').replace(/[&<>"']/g,c=>m[c]);
    }
  </script>
  
  <style>
    body { 
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }
    .card { border: none; border-radius: 12px; overflow: hidden; }
    .info-label { font-weight: 600; }
    ul li { margin-bottom: 5px; }
    .qr-box img { 
      border: 1px solid #ddd; 
      border-radius: 8px; 
      padding: 5px; 
      background-color: #fff;
      pointer-events: none;
      -webkit-user-drag: none;
      -khtml-user-drag: none;
      -moz-user-drag: none;
      -o-user-drag: none;
      user-drag: none;
    }
    [data-bs-theme="dark"] .qr-box img { background-color: #222; }
    
    /* Hide when printing or screenshotting */
    @media print { body { display: none !important; } }
    
    /* Loading state for bank info */
    #bank-info-container:empty::before,
    #qr-container:empty::before {
      content: '⏳ Đang tải...';
      color: #6c757d;
      font-style: italic;
    }
    
    /* Anti view-source protection */
    #secure-data {
      display: none !important;
      visibility: hidden !important;
      position: absolute !important;
      left: -9999px !important;
    }
  </style>
</head>
<body class="bg-body-secondary" oncopy="return false" oncut="return false" onpaste="return false">
<div class="container mt-5">

  <?php if ($justSentPending): ?>
    <div class="alert alert-success">✅ Đã gửi email hướng dẫn thanh toán tới: <b><?= h($tx['email']) ?></b></div>
  <?php elseif ($resent): ?>
    <div class="alert alert-<?= $justSentPending ? 'success':'warning' ?>">
      <?= $justSentPending ? '✅ Gửi lại email thành công.' : '⚠️ Không thể gửi email lúc này.' ?>
    </div>
  <?php endif; ?>

  <div class="card shadow-sm">
    <div class="card-header bg-primary text-white text-center py-3">
      <h4 class="mb-0">THÔNG TIN THANH TOÁN DỊCH VỤ VPN VIỆT NAM</h4>
    </div>
    <div class="card-body p-4">
      <div class="mb-3"><span class="info-label">👤 Khách hàng:</span> <?= h($tx['username']) ?></div>
      <div class="mb-3"><span class="info-label">✉️ Email:</span> <?= h($tx['email']) ?></div>
      <div class="mb-3"><span class="info-label">🆔 Mã giao dịch:</span> <?= h($tx['unique_code']) ?></div>
      <div class="mb-3"><span class="info-label">💰 Số tiền:</span> <span class="text-danger fw-bold"><?= number_format((int)$tx['amount_paid'], 0, ',', '.') ?> VND</span></div>
      <div class="mb-3"><span class="info-label">📊 Trạng thái:</span>
        <?php
        switch ($tx['status']) {
            case 'pending':      echo '<span class="badge bg-warning text-dark">Chờ xác nhận</span>'; break;
            case 'Thành công':
            case 'success':      echo '<span class="badge bg-success">Thành công</span>'; break;
            case 'Đã hủy':
            case 'cancelled':    echo '<span class="badge bg-danger">Đã hủy</span>'; break;
            default:             echo '<span class="badge bg-secondary">'.h($tx['status']).'</span>';
        }
        ?>
      </div>

      <?php if (!empty($tx['email']) && $tx['status'] === 'pending'): ?>
        <!-- Giữ nguyên là link GET, nhưng kèm chữ ký sig để server xác minh -->
        <a class="btn btn-outline-primary btn-sm mb-3"
           href="pay.php?code=<?= urlencode($transaction_code) ?>&resend=1&sig=<?= urlencode($sig_link_resend) ?>">
          ✉️ Gửi lại email hướng dẫn
        </a>
      <?php endif; ?>

      <hr>
      
      <?php if (!in_array($tx['status'], ['Đã hủy', 'cancelled'], true)): ?>
        <!-- Bank info will be injected by JavaScript -->
        <div id="bank-info-container">
          <h5 class="text-primary mb-3">🏦 Thông tin chuyển khoản:</h5>
          <p class="text-muted">
            <span class="spinner-border spinner-border-sm" role="status"></span>
            Đang tải thông tin thanh toán...
          </p>
        </div>
        
        <!-- QR will be injected by JavaScript -->
        <div id="qr-container"></div>

        <div class="alert alert-warning mt-4" role="alert">
          ⚠️ Vui lòng nhập <strong>đúng nội dung chuyển khoản</strong> để hệ thống tự động xác nhận!
        </div>
        <p class="text-muted">
          ✅ Sau khi quý khách hoàn tất chuyển khoản, hệ thống sẽ tự động cập nhật số dư trong vòng ít phút.
          Mỗi lệnh nạp tiền có hiệu lực trong 24 giờ kể từ thời điểm khởi tạo; quá thời hạn này nếu chưa nhận được xác nhận thanh toán, lệnh sẽ tự động hủy để đảm bảo an toàn.
          Cần hỗ trợ, vui lòng liên hệ hotline:
          <strong>0812.363.898 - 0826.003.926</strong> hoặc <a href="support.php">Trung Tâm Hỗ Trợ</a>.
        </p>
      <?php else: ?>
        <div class="alert alert-info mt-4" role="alert">
          ℹ️ Giao dịch này đã bị hủy. Vui lòng tạo lệnh nạp tiền mới nếu bạn muốn tiếp tục sử dụng dịch vụ.
        </div>
        <p class="text-muted">
          Cần hỗ trợ, vui lòng liên hệ hotline:
          <strong>0812.363.898 - 0826.003.926</strong> hoặc <a href="support.php">Trung Tâm Hỗ Trợ</a>.
        </p>
      <?php endif; ?>
    </div>
  </div>
</div>

<!-- Additional Security Layer -->
<script>
  // Watermark & Tracking
  (function(){
    const _0xwm=document.createElement('div');
    _0xwm.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;opacity:0.03;background:repeating-linear-gradient(45deg,transparent,transparent 100px,#000 100px,#000 101px)';
    document.body.appendChild(_0xwm);
    
    // Detect suspicious activities
    let _0xscore=0;
    document.addEventListener('keydown',function(e){
      if(e.ctrlKey||e.shiftKey||e.altKey)_0xscore++;
      if(_0xscore>10){window.location.href='about:blank';}
    });
    
    // Prevent iframe embedding
    if(window.top!==window.self){window.top.location=window.self.location;}
    
    // Monitor focus loss (potential DevTools)
    window.addEventListener('blur',function(){_0xscore+=2;});
    
    // Prevent drag and drop
    document.addEventListener('dragstart',e=>e.preventDefault());
    document.addEventListener('drop',e=>e.preventDefault());
    
    // Disable F11 fullscreen
    document.addEventListener('keydown',function(e){if(e.keyCode===122){e.preventDefault();}});
    
    // Monitor console access attempts
    Object.defineProperty(window,'console',{get:function(){_0xscore+=5;return{log:function(){},warn:function(){},error:function(){},info:function(){},debug:function(){},table:function(){},trace:function(){},clear:function(){}};}});
  })();
  
  // Final check before unload
  window.addEventListener('beforeunload',function(){console.clear();});
</script>

<!-- Invisible Security Marker -->
<div style="display:none;visibility:hidden;" data-secure-token="<?= bin2hex(random_bytes(16)) ?>" data-page-id="pay-<?= h($transaction_code) ?>"></div>

</body>
</html>
