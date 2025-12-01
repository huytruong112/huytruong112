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
    <title>Kết nối với V2Box</title>
    <link rel="icon" href="https://favicon.ico/iconvpnvietnam.png" type="image/x-icon">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"/>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
        }
        .container-box {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .app-icon {
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .app-icon i {
            font-size: 50px;
            color: white;
        }
        h1 {
            color: #333;
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
        }
        .config-name {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-weight: 600;
            color: #495057;
            border-left: 4px solid #667eea;
        }
        .qr-container {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: inline-block;
        }
        .qr-container img {
            max-width: 280px;
            width: 100%;
            height: auto;
            border-radius: 10px;
        }
        .btn-open-app {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            border: none;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        .btn-open-app:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
            color: white;
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
            padding: 12px 30px;
            border-radius: 50px;
            border: none;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
            color: white;
        }
        .instructions {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            text-align: left;
        }
        .instructions h5 {
            color: #856404;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .instructions ol {
            color: #856404;
            margin-bottom: 0;
            padding-left: 20px;
        }
        .instructions li {
            margin-bottom: 10px;
            line-height: 1.6;
        }
        .store-links {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .store-link {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 24px;
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            text-decoration: none;
            color: #333;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .store-link:hover {
            border-color: #667eea;
            color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .store-link i {
            font-size: 24px;
        }
        #status-message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            font-weight: 600;
            display: none;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @media (max-width: 576px) {
            .container-box {
                padding: 30px 20px;
            }
            h1 {
                font-size: 24px;
            }
            .btn-open-app {
                padding: 12px 30px;
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="container-box">
        <div class="app-icon">
            <i class="fas fa-shield-alt"></i>
        </div>
        <h1>Mở với V2Box</h1>
        <p class="subtitle">Kết nối VPN nhanh chóng và an toàn</p>
        
        <div class="config-name">
            <i class="fas fa-server"></i> <?= $configName ?>
        </div>

        <?php if (isset($qrCodePath)): ?>
        <div class="qr-container">
            <img src="<?= htmlspecialchars($qrCodePath) ?>" alt="QR Code">
        </div>
        <?php endif; ?>

        <button class="btn-open-app" id="openAppBtn" onclick="openV2Box()">
            <i class="fas fa-mobile-alt"></i> Mở Ứng Dụng V2Box
        </button>
        
        <a href="manage_services.php" class="btn-secondary">
            <i class="fas fa-arrow-left"></i> Quay lại
        </a>

        <div id="status-message"></div>

        <div class="instructions">
            <h5><i class="fas fa-info-circle"></i> Hướng dẫn sử dụng:</h5>
            <ol>
                <li><strong>iOS:</strong> Bấm "Mở Ứng Dụng V2Box" để tự động mở app. Nếu chưa cài đặt, bạn sẽ được chuyển đến App Store.</li>
                <li><strong>Android:</strong> Bấm "Mở Ứng Dụng V2Box" để tự động mở app. Nếu chưa cài đặt, bạn sẽ được chuyển đến Google Play.</li>
                <li><strong>Cách khác:</strong> Quét mã QR trực tiếp từ ứng dụng V2Box đã cài đặt trên thiết bị của bạn.</li>
            </ol>
            
            <div class="store-links">
                <a href="https://apps.apple.com/app/v2box/id6446814690" target="_blank" class="store-link" id="appStoreLink">
                    <i class="fab fa-apple"></i>
                    <span>App Store</span>
                </a>
                <a href="https://play.google.com/store/apps/details?id=dev.hexasoftware.v2box" target="_blank" class="store-link" id="playStoreLink">
                    <i class="fab fa-google-play"></i>
                    <span>Google Play</span>
                </a>
            </div>
        </div>
    </div>

    <script>
        // VLESS URI và thông tin cấu hình
        const vlessUri = <?= json_encode($vlessUri) ?>;
        const vlessUriEncoded = <?= json_encode($vlessUriEncoded) ?>;

        // Detect thiết bị
        function detectDevice() {
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            
            if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
                return 'iOS';
            }
            
            if (/android/i.test(userAgent)) {
                return 'Android';
            }
            
            return 'Other';
        }

        // Hiển thị thông báo trạng thái
        function showStatus(message, type = 'success') {
            const statusDiv = document.getElementById('status-message');
            statusDiv.innerHTML = message;
            statusDiv.className = type === 'success' ? 'status-success' : 'status-warning';
            statusDiv.style.display = 'block';
        }

        // Mở ứng dụng V2Box với cấu hình tự động
        function openV2Box() {
            const device = detectDevice();
            const btn = document.getElementById('openAppBtn');
            
            // Vô hiệu hóa nút trong khi xử lý
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Đang mở ứng dụng...';

            // Store links
            const appStoreUrl = 'https://apps.apple.com/app/v2box/id6446814690';
            const playStoreUrl = 'https://play.google.com/store/apps/details?id=dev.hexasoftware.v2box';

            if (device === 'iOS') {
                // iOS - Mở V2Box với deep link và tự động import config
                // Deep link với VLESS URI để tự động thêm vào app
                const deepLink = vlessUri; // Sử dụng trực tiếp VLESS URI
                
                let appOpened = false;
                const startTime = Date.now();

                // Lắng nghe sự kiện blur (khi chuyển sang app khác)
                const handleBlur = () => {
                    appOpened = true;
                };
                window.addEventListener('blur', handleBlur);

                // Lắng nghe visibility change (phương pháp chính xác hơn)
                const handleVisibilityChange = () => {
                    if (document.hidden) {
                        appOpened = true;
                        clearTimeout(checkTimer);
                        showStatus('✅ Đã mở V2Box và thêm cấu hình thành công!', 'success');
                        setTimeout(() => {
                            btn.disabled = false;
                            btn.innerHTML = '<i class="fas fa-mobile-alt"></i> Mở Ứng Dụng V2Box';
                        }, 2000);
                        window.removeEventListener('blur', handleBlur);
                        document.removeEventListener('visibilitychange', handleVisibilityChange);
                    }
                };
                document.addEventListener('visibilitychange', handleVisibilityChange);

                // Thử mở ứng dụng
                window.location.href = deepLink;

                // Kiểm tra sau 2 giây
                const checkTimer = setTimeout(() => {
                    window.removeEventListener('blur', handleBlur);
                    document.removeEventListener('visibilitychange', handleVisibilityChange);
                    
                    if (!appOpened && !document.hidden) {
                        // App không mở được - chưa cài V2Box
                        showStatus('⚠️ Chưa cài đặt V2Box. Đang chuyển đến App Store...', 'warning');
                        setTimeout(() => {
                            window.location.href = appStoreUrl;
                        }, 1000);
                    }
                }, 2000);

            } else if (device === 'Android') {
                // Android - Mở V2Box với Intent và tự động import config
                // Intent với VLESS URI để tự động thêm vào app
                const intent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=dev.hexasoftware.v2box;end`;
                
                let appOpened = false;
                const startTime = Date.now();

                // Lắng nghe sự kiện blur
                const handleBlur = () => {
                    appOpened = true;
                };
                window.addEventListener('blur', handleBlur);

                // Lắng nghe visibility change
                const handleVisibilityChange = () => {
                    if (document.hidden) {
                        appOpened = true;
                        clearTimeout(checkTimer);
                        showStatus('✅ Đã mở V2Box và thêm cấu hình thành công!', 'success');
                        setTimeout(() => {
                            btn.disabled = false;
                            btn.innerHTML = '<i class="fas fa-mobile-alt"></i> Mở Ứng Dụng V2Box';
                        }, 2000);
                        window.removeEventListener('blur', handleBlur);
                        document.removeEventListener('visibilitychange', handleVisibilityChange);
                    }
                };
                document.addEventListener('visibilitychange', handleVisibilityChange);

                // Thử mở ứng dụng
                window.location.href = intent;

                // Kiểm tra sau 2 giây
                const checkTimer = setTimeout(() => {
                    window.removeEventListener('blur', handleBlur);
                    document.removeEventListener('visibilitychange', handleVisibilityChange);
                    
                    if (!appOpened && !document.hidden) {
                        // App không mở được - chưa cài V2Box
                        showStatus('⚠️ Chưa cài đặt V2Box. Đang chuyển đến Google Play...', 'warning');
                        setTimeout(() => {
                            window.location.href = playStoreUrl;
                        }, 1000);
                    }
                }, 2000);

            } else {
                // Desktop hoặc thiết bị khác
                showStatus('⚠️ V2Box chỉ khả dụng trên iOS và Android. Vui lòng sử dụng thiết bị di động hoặc quét mã QR bằng ứng dụng.', 'warning');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-mobile-alt"></i> Mở Ứng Dụng V2Box';
            }
        }

        // Tự động copy URI vào clipboard
        function copyToClipboard() {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(vlessUri)
                    .then(() => {
                        console.log('✓ VLESS URI đã được copy vào clipboard');
                    })
                    .catch(err => {
                        console.error('Lỗi khi copy:', err);
                    });
            }
        }

        // Copy URI và hiển thị hướng dẫn khi trang load
        window.addEventListener('load', () => {
            // Copy URI để người dùng có thể paste thủ công nếu cần
            copyToClipboard();
            
            // Hiển thị thông báo hướng dẫn
            showStatus('📱 Bấm nút "Mở Ứng Dụng V2Box" để tự động thêm cấu hình vào ứng dụng.', 'warning');
        });

        // Xử lý khi quay lại từ App Store/Play Store
        let wasHidden = false;
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                wasHidden = true;
            } else if (wasHidden) {
                // User quay lại từ Store
                const btn = document.getElementById('openAppBtn');
                if (btn.disabled) {
                    btn.disabled = false;
                }
                btn.innerHTML = '<i class="fas fa-mobile-alt"></i> Thử Lại';
                showStatus('💡 Nếu bạn vừa cài đặt V2Box, hãy bấm "Thử Lại" để tự động thêm cấu hình.', 'warning');
                wasHidden = false;
            }
        });

        // Tự động mở app nếu có tham số auto=1
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('auto') === '1') {
            setTimeout(() => {
                openV2Box();
            }, 500);
        }
    </script>
</body>
</html>
