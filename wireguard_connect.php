<?php
session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit();
}

require_once 'db.php';
$user_id = (int)$_SESSION['user_id'];

// Lấy ID của service
$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($id <= 0) {
    http_response_code(400);
    die("Invalid ID");
}

// Lấy thông tin WireGuard config
$sql = "SELECT us.id, us.server, us.package_id, us.qr_data, us.public_key, 
               sp.package_name
        FROM user_services us
        JOIN service_packages sp ON us.package_id = sp.id
        WHERE us.id = ? AND us.user_id = ? AND us.status != 'canceled'";
$st = $pdo->prepare($sql);
$st->execute([$id, $user_id]);
$service = $st->fetch(PDO::FETCH_ASSOC);

if (!$service) {
    http_response_code(404);
    die("WireGuard config not found");
}

// Kiểm tra trạng thái và qr_data
$qrData = trim((string)($service['qr_data'] ?? ''));
$publicKey = trim((string)($service['public_key'] ?? ''));

if (empty($qrData)) {
    http_response_code(400);
    die("WireGuard config chưa sẵn sàng. Vui lòng đợi kích hoạt hoàn tất.");
}

$configName = htmlspecialchars($service['package_name'] ?: 'WireGuard VPN', ENT_QUOTES, 'UTF-8');
$serverName = htmlspecialchars($service['server'] ?: 'Server', ENT_QUOTES, 'UTF-8');

// Encode config cho các platform
$configBase64 = base64_encode($qrData);
$configUrlEncoded = urlencode($qrData);

// Tạo QR Code
$qrCodeDir = __DIR__ . '/qrcodes/';
if (!is_dir($qrCodeDir)) mkdir($qrCodeDir, 0700, true);

$qrCodePath = null;
$qrLibPath = $_SERVER['DOCUMENT_ROOT'] . '/phpqrcode/qrlib.php';
if (file_exists($qrLibPath)) {
    require_once $qrLibPath;
    if (class_exists('QRcode')) {
        $pngFile = $qrCodeDir . 'wg_'.$id.'.png';
        if (!file_exists($pngFile)) {
            QRcode::png($qrData, $pngFile, QR_ECLEVEL_L, 6);
        }
        $qrCodePath = 'qrcodes/wg_'.$id.'.png';
    }
}

?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kết nối với WireGuard</title>
    <link rel="icon" href="https://favicon.ico/iconvpnvietnam.png" type="image/x-icon">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"/>
    <link rel="stylesheet" href="css/wireguard-connect.css">
</head>
<body>
    <div class="container-box">
        <div class="app-icon wireguard">
            <i class="fas fa-shield-halved"></i>
        </div>
        <h1>Kết Nối WireGuard VPN</h1>
        <p class="subtitle">Tự động thêm cấu hình vào ứng dụng WireGuard</p>
        
        <div class="config-name">
            <i class="fas fa-server"></i> <?= $configName ?> - <?= $serverName ?>
        </div>

        <?php if ($qrCodePath): ?>
        <div class="qr-container">
            <img src="<?= htmlspecialchars($qrCodePath) ?>" alt="QR Code">
        </div>
        <?php endif; ?>

        <button class="btn-open-app wireguard" id="openAppBtn" onclick="openWireGuard()">
            <i class="fas fa-plug"></i> Kết Nối Ngay
        </button>
        
        <a href="manage_services.php" class="btn-secondary">
            <i class="fas fa-arrow-left"></i> Quay lại
        </a>

        <div id="status-message"></div>

        <div class="instructions">
            <h5><i class="fas fa-info-circle"></i> Hướng dẫn sử dụng:</h5>
            <ol>
                <li><strong>Đã cài WireGuard:</strong> Bấm "Kết Nối Ngay" → Ứng dụng WireGuard sẽ tự động mở và thêm cấu hình VPN vào danh sách.</li>
                <li><strong>Chưa cài WireGuard:</strong> Bấm "Kết Nối Ngay" → Hệ thống sẽ tự động chuyển đến App Store (iOS) hoặc Google Play (Android) để tải ứng dụng.</li>
                <li><strong>Sau khi cài đặt:</strong> Quay lại trang này và bấm "Thử Lại" để tự động thêm cấu hình vào WireGuard.</li>
                <li><strong>Cách khác:</strong> Quét mã QR trực tiếp từ ứng dụng WireGuard đã cài đặt trên thiết bị của bạn.</li>
            </ol>
            
            <div class="config-details">
                <h6><i class="fas fa-key"></i> Public Key:</h6>
                <div class="public-key-display">
                    <code id="publicKeyText"><?= htmlspecialchars($publicKey) ?></code>
                    <button class="btn-copy-small" onclick="copyPublicKey()">
                        <i class="fa fa-copy"></i>
                    </button>
                </div>
            </div>
            
            <div class="store-links">
                <a href="https://apps.apple.com/us/app/wireguard/id1441195209" target="_blank" class="store-link" id="appStoreLink">
                    <i class="fab fa-apple"></i>
                    <span>App Store (iOS)</span>
                </a>
                <a href="https://play.google.com/store/apps/details?id=com.wireguard.android" target="_blank" class="store-link" id="playStoreLink">
                    <i class="fab fa-google-play"></i>
                    <span>Google Play (Android)</span>
                </a>
            </div>
        </div>
    </div>

    <script src="js/wireguard-connect.js"></script>
    <script>
        // Khởi tạo cấu hình từ PHP
        initializeWireGuardConfig(
            <?= json_encode($qrData) ?>,
            <?= json_encode($configBase64) ?>,
            <?= json_encode($publicKey) ?>
        );
    </script>
</body>
</html>
