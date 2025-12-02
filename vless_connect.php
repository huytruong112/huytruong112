<?php
session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit();
}

require_once 'db.php';
$user_id = (int)$_SESSION['user_id'];

// Lấy ID của VLESS config
$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($id <= 0) {
    http_response_code(400);
    die("Invalid ID");
}

// Lấy thông tin VLESS config
$sql = "SELECT vc.*, us.user_id
        FROM vless_configs vc
        JOIN user_services us ON us.id = vc.user_service_id
        WHERE vc.id = ? AND us.user_id = ?";
$st = $pdo->prepare($sql);
$st->execute([$id, $user_id]);
$v = $st->fetch(PDO::FETCH_ASSOC);

if (!$v) {
    http_response_code(404);
    die("VLESS config not found");
}

// Xây dựng VLESS URI
function build_vless_uri_simple(array $c): string {
    $uuid = $c['uuid'];
    $addr = $c['address'];
    $port = (int)$c['port'];
    $name = rawurlencode($c['name'] ?: 'VLESS');
    $sec  = $c['security'] ?: 'reality';
    $net  = $c['network']  ?: 'tcp';
    $sni  = trim((string)($c['sni'] ?? ''));
    $flow = trim((string)($c['flow'] ?? ''));
    $pbk  = trim((string)($c['reality_pubkey'] ?? ''));
    $sid  = trim((string)($c['reality_shortid'] ?? ''));
    $path = trim((string)($c['path'] ?? ''));
    $host = trim((string)($c['host_header'] ?? ''));
    $alpn = trim((string)($c['alpn'] ?? ''));

    $q = ['encryption' => 'none', 'type' => $net];

    if ($flow !== '') $q['flow'] = $flow;

    if ($sec === 'tls') {
        $q['security'] = 'tls';
        if ($sni !== '')  $q['sni'] = $sni;
        if ($alpn !== '') $q['alpn'] = $alpn;
        if ($host !== '') $q['host'] = $host;
    } elseif ($sec === 'reality') {
        $q['security'] = 'reality';
        if ($sni !== '')  $q['sni'] = $sni;
        if ($pbk !== '')  $q['pbk'] = $pbk;
        if ($sid !== '')  $q['sid'] = $sid;
        if ($alpn !== '') $q['alpn'] = $alpn;
    } else {
        $q['security'] = 'none';
    }

    if ($net === 'ws' || $net === 'h2') {
        if ($path !== '') $q['path'] = $path;
        if ($host !== '') $q['host'] = $host;
    } elseif ($net === 'grpc') {
        if ($path !== '') $q['serviceName'] = $path;
        if ($host !== '') $q['authority']   = $host;
    }

    $query = http_build_query($q, '', '&', PHP_QUERY_RFC3986);
    return "vless://{$uuid}@{$addr}:{$port}?{$query}#{$name}";
}

$vlessUri = build_vless_uri_simple($v);
$vlessUriEncoded = urlencode($vlessUri);
$configName = htmlspecialchars($v['name'] ?: 'VLESS', ENT_QUOTES, 'UTF-8');

// Tạo QR Code cho VLESS
$qrCodeDir = __DIR__ . '/qrcodes/';
if (!is_dir($qrCodeDir)) mkdir($qrCodeDir, 0700, true);

$qrLibPath = $_SERVER['DOCUMENT_ROOT'] . '/phpqrcode/qrlib.php';
if (file_exists($qrLibPath)) {
    require_once $qrLibPath;
    if (class_exists('QRcode')) {
        $pngFile = $qrCodeDir . 'vless_'.$id.'.png';
        if (!file_exists($pngFile)) {
            QRcode::png($vlessUri, $pngFile, QR_ECLEVEL_L, 6);
        }
        $qrCodePath = 'qrcodes/vless_'.$id.'.png';
    }
}

?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thêm Cấu Hình VPN</title>
    <link rel="icon" href="https://favicon.ico/iconvpnvietnam.png" type="image/x-icon">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"/>
    <link rel="stylesheet" href="css/vless-connect.css">
</head>
<body>
    <div class="container-box">
        <div class="app-icon">
            <i class="fas fa-shield-alt"></i>
        </div>
        <h1>Thêm Cấu Hình VPN</h1>
        <p class="subtitle">Tự động thêm vào ứng dụng Streisand hoặc sing-box</p>
        
        <div class="config-name">
            <i class="fas fa-server"></i> <?= $configName ?>
        </div>

        <?php if (isset($qrCodePath)): ?>
        <div class="qr-container">
            <img src="<?= htmlspecialchars($qrCodePath) ?>" alt="QR Code">
        </div>
        <?php endif; ?>

        <button class="btn-open-app" id="openAppBtn" onclick="openVPNApp()">
            <i class="fas fa-plus-circle"></i> Thêm Cấu Hình
        </button>
        
        <a href="manage_services.php" class="btn-secondary">
            <i class="fas fa-arrow-left"></i> Quay lại
        </a>

        <div id="status-message"></div>

        <div class="instructions">
            <h5><i class="fas fa-info-circle"></i> Hướng dẫn sử dụng:</h5>
            <ol>
                <li><strong>Đã cài Streisand hoặc sing-box:</strong> Bấm "Thêm Cấu Hình" → Ứng dụng sẽ tự động mở và thêm cấu hình VLESS vào danh sách.</li>
                <li><strong>Chưa cài ứng dụng:</strong> Bấm "Thêm Cấu Hình" → Hệ thống sẽ tự động chuyển đến App Store (iOS) hoặc Google Play (Android) để tải ứng dụng.</li>
                <li><strong>Sau khi cài đặt:</strong> Quay lại trang này và bấm "Thử Lại" để tự động thêm cấu hình.</li>
                <li><strong>Cách khác:</strong> Quét mã QR trực tiếp từ ứng dụng đã cài đặt trên thiết bị của bạn.</li>
            </ol>
            
            <div class="app-priority-info">
                <h6><i class="fas fa-layer-group"></i> Thứ tự ưu tiên:</h6>
                <ol>
                    <li>Thử mở <strong>Streisand</strong> trước</li>
                    <li>Nếu không có → Thử mở <strong>sing-box</strong></li>
                    <li>Nếu không có → Chuyển đến Store để tải</li>
                </ol>
            </div>
            
            <div class="store-links">
                <a href="https://apps.apple.com/app/streisand/id6450534064" target="_blank" class="store-link">
                    <i class="fab fa-apple"></i>
                    <span>Streisand (iOS)</span>
                </a>
                <a href="https://play.google.com/store/apps/details?id=com.github.shadowsocks.tv.vpn" target="_blank" class="store-link">
                    <i class="fab fa-google-play"></i>
                    <span>Streisand (Android)</span>
                </a>
                <a href="https://apps.apple.com/app/sing-box/id6451272673" target="_blank" class="store-link">
                    <i class="fab fa-apple"></i>
                    <span>sing-box (iOS)</span>
                </a>
                <a href="https://play.google.com/store/apps/details?id=io.nekohasekai.sfa" target="_blank" class="store-link">
                    <i class="fab fa-google-play"></i>
                    <span>sing-box (Android)</span>
                </a>
            </div>
        </div>
    </div>

    <script src="js/vless-connect.js"></script>
    <script>
        // Khởi tạo cấu hình từ PHP
        initializeConfig(
            <?= json_encode($vlessUri) ?>,
            <?= json_encode($vlessUriEncoded) ?>
        );
    </script>
</body>
</html>
