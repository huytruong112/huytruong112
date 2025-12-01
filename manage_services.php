<?php

session_start();

if (!isset($_SESSION['user_id'])) {

    header('Location: login.php');

    exit();

}



// TẠO CSRF TOKEN

if (!isset($_SESSION['csrf_token'])) {

    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));

}



// SỬA LỖI: Sử dụng file db.php với PDO

require_once 'db.php';

$user_id = (int)$_SESSION['user_id'];



/* ===========================================================

   QRCode (WireGuard & VLESS)

   =========================================================== */

$qrLibPath = $_SERVER['DOCUMENT_ROOT'] . '/phpqrcode/qrlib.php';

if (!file_exists($qrLibPath)) die("Lỗi hệ thống QR.");

require_once $qrLibPath;

if (!class_exists('QRcode')) die("Hệ thống QR lỗi.");



$qrCodeDir    = __DIR__ . '/qrcodes/';

$qrCodeWebDir = 'qrcodes/';

if (!is_dir($qrCodeDir)) mkdir($qrCodeDir, 0700, true);



$msg = $_GET['msg'] ?? '';



/* ===========================================================

   Helper: escape

   =========================================================== */

function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }



/* ===========================================================

   Helper: VLESS URI Builder

   Input: associative array row from vless_configs

   =========================================================== */

function build_vless_uri(array $c): string {

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



/* ===========================================================

   Endpoint: VLESS Download (txt / yaml)

   URL: ?download_vless=txt&id=123  hoặc  ?download_vless=yaml&id=123

   =========================================================== */

if (isset($_GET['download_vless']) && isset($_GET['id'])) {

    $fmt = strtolower(trim($_GET['download_vless']));

    $id  = (int)$_GET['id'];



    // SỬA LỖI: Chuyển đổi từ mysqli sang PDO

    $sql = "SELECT vc.*, us.user_id

            FROM vless_configs vc

            JOIN user_services us ON us.id = vc.user_service_id

            WHERE vc.id = ? AND us.user_id = ?";

    $st = $pdo->prepare($sql);

    $st->execute([$id, $user_id]);

    $v = $st->fetch(PDO::FETCH_ASSOC);

    if (!$v) { http_response_code(404); echo "Not found"; exit; }



    $uri = build_vless_uri($v);



    if ($fmt === 'txt') {

        header('Content-Type: text/plain; charset=utf-8');

        header('Content-Disposition: attachment; filename="vless-'.$id.'.txt"');

        echo $uri; exit;

    }

    if ($fmt === 'yaml' || $fmt === 'yml') {

        $yaml = [];

        $yaml[] = 'proxies:';

        $yaml[] = '- name: "'.str_replace('"','\"', ($v['name'] ?: 'VLESS')).'"';

        $yaml[] = '  type: vless';

        $yaml[] = '  server: '.$v['address'];

        $yaml[] = '  port: '.(int)$v['port'];

        $yaml[] = '  uuid: '.$v['uuid'];

        $yaml[] = '  udp: true';

        $yaml[] = '  network: '.($v['network'] ?: 'tcp');



        $sec = $v['security'] ?: 'none';

        if ($sec === 'tls') {

            $yaml[] = '  tls: true';

            if (!empty($v['sni']))  $yaml[] = '  servername: '.$v['sni'];

            if (!empty($v['alpn'])) {

                $al = array_map('trim', explode(',', $v['alpn']));

                $yaml[] = '  alpn: ['.implode(', ', array_map(fn($a)=>'"'.str_replace('"','\"',$a).'"', $al)).']';

            }

        } elseif ($sec === 'reality') {

            $yaml[] = '  tls: true';

            $yaml[] = '  reality-opts:';

            if (!empty($v['reality_pubkey']))  $yaml[] = '    public-key: "'.str_replace('"','\"',$v['reality_pubkey']).'"';

            if (!empty($v['reality_shortid'])) $yaml[] = '    short-id: "'.str_replace('"','\"',$v['reality_shortid']).'"';

            $sni = $v['sni'] ?: $v['host_header'];

            if (!empty($sni)) $yaml[] = '  servername: "'.str_replace('"','\"',$sni).'"';

            if (!empty($v['alpn'])) {

                $al = array_map('trim', explode(',', $v['alpn']));

                $yaml[] = '  alpn: ['.implode(', ', array_map(fn($a)=>'"'.str_replace('"','\"',$a).'"', $al)).']';

            }

        } else {

            $yaml[] = '  tls: false';

        }

        if (!empty($v['flow'])) $yaml[] = '  flow: "'.str_replace('"','\"',$v['flow']).'"';



        $path = trim((string)$v['path']);

        $host = trim((string)$v['host_header']);

        if ($v['network'] === 'ws') {

            $yaml[] = '  ws-opts:';

            if ($path !== '') $yaml[] = '    path: "'.str_replace('"','\"',$path).'"';

            if ($host !== '') $yaml[] = '    headers: { Host: "'.str_replace('"','\"',$host).'" }';

        } elseif ($v['network'] === 'grpc') {

            $yaml[] = '  grpc-opts:';

            if ($path !== '') $yaml[] = '    grpc-service-name: "'.str_replace('"','\"',$path).'"';

            if ($host !== '') $yaml[] = '    authority: "'.str_replace('"','\"',$host).'"';

        } elseif ($v['network'] === 'h2') {

            $yaml[] = '  h2-opts:';

            if ($path !== '') $yaml[] = '    path: "'.str_replace('"','\"',$path).'"';

            if ($host !== '') $yaml[] = '    host: ["'.str_replace('"','\"',$host).'"]';

        }



        header('Content-Type: text/yaml; charset=utf-8');

        header('Content-Disposition: attachment; filename="vless-'.$id.'.yaml"');

        echo implode("\n", $yaml)."\n"; exit;

    }



    http_response_code(400);

    echo "download_vless must be txt|yaml";

    exit;

}



/* ===========================================================

   Endpoint: VLESS QR as PNG (server-side)

   URL: ?vless_qr=123

   =========================================================== */

if (isset($_GET['vless_qr'])) {

    $id = (int)$_GET['vless_qr'];

    // SỬA LỖI: Chuyển đổi từ mysqli sang PDO

    $sql = "SELECT vc.*, us.user_id

            FROM vless_configs vc

            JOIN user_services us ON us.id = vc.user_service_id

            WHERE vc.id = ? AND us.user_id = ?";

    $st = $pdo->prepare($sql);

    $st->execute([$id, $user_id]);

    $v = $st->fetch(PDO::FETCH_ASSOC);

    if (!$v) { http_response_code(404); exit('Not found'); }

    $uri = build_vless_uri($v);



    // cache file

    $pngFile = $qrCodeDir . 'vless_'.$id.'.png';

    if (!file_exists($pngFile)) {

        QRcode::png($uri, $pngFile, QR_ECLEVEL_L, 4);

    }

    header('Content-Type: image/png');

    readfile($pngFile);

    exit;

}



/* ===========================================================

   Tải danh sách dịch vụ của user

   =========================================================== */

// SỬA LỖI: Chuyển đổi từ mysqli sang PDO

$stmt = $pdo->prepare(

    "SELECT us.id, us.server, us.payment_date, us.expiry_date, us.status, us.is_activated,

            us.qr_data, us.public_key, us.user_id,

            sp.package_name

     FROM user_services us

     JOIN service_packages sp ON us.package_id = sp.id

     WHERE us.user_id = ?

     ORDER BY us.payment_date DESC"

);

$stmt->execute([$user_id]);



$active_services = [];

$expired_services = [];

$canceled_services = [];

$all_service_ids = [];



// SỬA LỖI: Thay đổi vòng lặp để phù hợp với PDO

while ($service = $stmt->fetch(PDO::FETCH_ASSOC)) {

    $all_service_ids[] = (int)$service['id'];

    if ($service['status'] === 'canceled') {

        $canceled_services[] = $service;

        continue;

    }

    $expiry_time = isset($service['expiry_date']) ? strtotime($service['expiry_date']) : 0;

    if ($expiry_time && time() > $expiry_time) {

        $expired_services[] = $service;

    } else {

        $active_services[] = $service;

    }

}



/* ===========================================================

   Lấy toàn bộ VLESS của các dịch vụ hiện có (enabled=1)

   Group theo user_service_id: $vlessByService[$sid] = [rows...]

   =========================================================== */

$vlessByService = [];

if (count($all_service_ids)) {

    $ids = array_map('intval', $all_service_ids);

    $ids = array_filter($ids, fn($x)=>$x>0);

    if (count($ids)) {

        // SỬA LỖI: Chuyển đổi từ mysqli sang PDO

        $in_placeholders = implode(',', array_fill(0, count($ids), '?'));

        $sql = "

            SELECT vc.*

            FROM vless_configs vc

            WHERE vc.enabled = 1 AND vc.user_service_id IN ($in_placeholders)

            ORDER BY vc.id DESC

        ";

        $stmt_vless = $pdo->prepare($sql);

        $stmt_vless->execute($ids);

        while ($row = $stmt_vless->fetch(PDO::FETCH_ASSOC)) {

            $sid = (int)$row['user_service_id'];

            if (!isset($vlessByService[$sid])) $vlessByService[$sid] = [];

            $vlessByService[$sid][] = $row;

        }

    }

}



/* ===========================================================

   Render 1 dòng dịch vụ (giữ nguyên cũ + cột VLESS mới + Gia hạn mọi lúc với UI đẹp)

   =========================================================== */

function render_service_row($service, $qrCodeWebDir, $qrCodeDir, $vlessByService, $csrf_token) {

    $status = "Chưa Xác Định";

    $status_class = "";

    $expiry_raw = $service['expiry_date'] ?? null;

    $service_copy = $service; // copy để không thay đổi tham chiếu gốc



    if ($service['status'] === 'canceled') {

        $status = "Đã hủy";

        $status_class = "status-canceled";

        $service_copy['public_key'] = '';

        $service_copy['qr_data'] = '';

    } else if ($expiry_raw) {

        $expiry_time = strtotime($expiry_raw);

        if (time() > $expiry_time) {

            $status = "Hết Hạn";

            $status_class = "status-expired";

            $service_copy['public_key'] = '';

            $service_copy['qr_data'] = '';

        } else {

            $status = "Đang Hoạt Động";

            $status_class = "status-active";

        }

    }



    $payment_date = (!empty($service['payment_date'])) ? date("d-m-Y", strtotime($service['payment_date'])) : '';

    $expiry_date  = (!empty($service['expiry_date']))  ? date("d-m-Y", strtotime($service['expiry_date']))  : '';



    // WireGuard QR/File cũ

    $qrData = $service_copy['qr_data'] ?? '';

    $qrFileName = '';

    if (!empty($qrData)) {

        $qrFileName = $qrCodeWebDir . 'qr_' . $service['id'] . '.png';

        $qrFilePath = $qrCodeDir . 'qr_' . $service['id'] . '.png';

        if (!file_exists($qrFilePath)) {

            QRcode::png($qrData, $qrFilePath, QR_ECLEVEL_L, 4);

        }

    }



    // VLESS list cho dịch vụ

    $sid = (int)$service['id'];

    $vlessList = $vlessByService[$sid] ?? [];



    // Tính số ngày còn lại trước khi hết hạn

    $days_left = null;

    if ($expiry_raw) {

        $expiry_time = strtotime($expiry_raw);

        $current_time = time();

        $seconds_left = $expiry_time - $current_time;

        $days_left = ceil($seconds_left / 86400);

    }



    ?>

    <tr>

      <td><?= h($service['package_name'] ?? '') ?></td>

      <td><?= h($service['server'] ?? '') ?></td>

      <td><?= h($payment_date) ?></td>

      <td><?= h($expiry_date) ?></td>

      <td class="<?= h($status_class) ?>"><?= h($status) ?></td>



      <!-- QR WireGuard (cũ) -->

      <td>

        <?php if ($status === "Hết Hạn"): ?>

            <span style="color:#c00;">Gói dịch vụ đã hết hạn, vui lòng gia hạn.</span>

        <?php elseif ($qrFileName && $status !== "Đã hủy"): ?>

            <img class="qr-code-img" src="<?= h($qrFileName) ?>" alt="QR Code">

        <?php elseif ($status === "Đã hủy"): ?>

            <span style="color:#c00;">Đã xóa</span>

        <?php else: ?>

            Đang hoàn tất kích hoạt trong 2 phút.

        <?php endif; ?>

      </td>



      <!-- Public Key WireGuard (cũ) -->

      <td>

        <?php if ($status === "Hết Hạn"): ?>

            <span style="color:#c00;">Gói dịch vụ đã hết hạn, vui lòng gia hạn.</span>

        <?php elseif ($service['is_activated'] && !empty($service_copy['public_key']) && $status !== "Đã hủy"): ?>

            <div class="public-key-box">

              <pre id="pk<?= (int)$service['id'] ?>"><?= h($service_copy['public_key']) ?></pre>

            </div>

            <button class="copy-btn" onclick="copyBlock('pk<?= (int)$service['id'] ?>')"><i class="fa fa-copy"></i> Sao chép</button>

            <a class="copy-btn" href="download_public_key.php?service_id=<?= (int)$service['id'] ?>"><i class="fa fa-download"></i> Tải xuống</a>

        <?php elseif ($status === "Đã hủy"): ?>

            <span style="color:#c00;">Đã xóa</span>

        <?php elseif ($service['is_activated']): ?>

            Public Key không khả dụng

        <?php else: ?>

            Đang được xử lý kích hoạt trong 2 phút.

        <?php endif; ?>

      </td>



      <!-- VLESS (MỚI) -->

      <td>

        <?php if ($status !== "Đang Hoạt Động"): ?>

          <span class="text-muted">VLESS chỉ khả dụng khi gói đang hoạt động.</span>

        <?php elseif (!count($vlessList)): ?>

          <span class="text-muted">Chưa có cấu hình VLESS cho gói này.</span>

        <?php else: ?>

          <div class="vless-list">

            <?php foreach ($vlessList as $v): ?>

              <?php

                // Xây URI để hiển thị nhanh (không tải file)

                $uri = build_vless_uri($v);

                $vid = (int)$v['id'];

                $nm  = $v['name'] ?: 'VLESS';

              ?>

              <div class="vless-item">

                <div class="vless-title"><strong><?= h($nm) ?></strong> <small class="text-muted">(<?= h($v['address']) ?>:<?= (int)$v['port'] ?>)</small></div>

                <div class="vless-actions">

                  <button class="btn btn-sm btn-outline-primary" onclick="copyText(`<?= h($uri) ?>`)"><i class="fa fa-copy"></i> Copy URL</button>

                  <a class="btn btn-sm btn-outline-success" href="vless_open.php?id=<?= $vid ?>"><i class="fa fa-qrcode"></i> QR CODE</a>

                  <a class="btn btn-sm btn-outline-dark" href="?download_vless=txt&id=<?= $vid ?>"><i class="fa fa-file-text"></i> .TXT</a>

                  <a class="btn btn-sm btn-outline-dark" href="?download_vless=yaml&id=<?= $vid ?>"><i class="fa fa-file-code"></i> .YAML</a>

                </div>

              </div>

            <?php endforeach; ?>

          </div>

        <?php endif; ?>

      </td>



      <!-- Thao tác gói -->

      <td>

        <?php if ($status === 'Đang Hoạt Động'): ?>

          <div class="action-buttons">

            <!-- Nút Hủy -->

            <a href="cancel_service.php?id=<?= (int)$service['id'] ?>"

               onclick="return confirm('Quý khách có muốn hủy gói dịch vụ này không?');"

               class="btn-action btn-cancel">

              <i class="fa fa-ban"></i> Hủy Gói

            </a>

            

            <!-- Form Gia hạn đẹp với CSRF Token -->

            <div class="renew-box">

              <div class="renew-header">

                <i class="fa fa-clock-rotate-left"></i> Gia Hạn Dịch Vụ

              </div>

              <form action="renew_service.php" method="GET" class="renew-form-modern"

                    onsubmit="return confirm('Xác nhận gia hạn gói này?');">

                <input type="hidden" name="csrf_token" value="<?= h($csrf_token) ?>">

                <input type="hidden" name="id" value="<?= (int)$service['id'] ?>">

                <div class="renew-content">

                  <select name="period" class="renew-select" id="period<?= (int)$service['id'] ?>">

                    <option value="1">1 tháng</option>

                    <option value="3">3 tháng</option>

                    <option value="6">6 tháng</option>

                    <option value="8">8 tháng</option>

                    <option value="12">12 tháng</option>

                    <option value="18">18 tháng</option>

                    <option value="36">36 tháng</option>

                  </select>

                  <button type="submit" class="btn-action btn-renew">

                    <i class="fa fa-arrow-rotate-right"></i> Gia Hạn

                  </button>

                </div>

              </form>

              

              <?php if ($days_left !== null && $days_left <= 5): ?>

                <div class="expiry-warning">

                  <i class="fa fa-triangle-exclamation"></i> Còn <strong><?= $days_left ?> ngày</strong> là hết hạn!

                </div>

              <?php endif; ?>

            </div>

          </div>

          

        <?php elseif ($status === 'Đã hủy'): ?>

          <span style="color:#c00;font-weight:600;">Đã Huỷ Gói</span>

        <?php else: ?>

          <!-- Gói hết hạn - Form gia hạn đẹp với CSRF Token -->

          <div class="renew-box">

            <div class="renew-header expired">

              <i class="fa fa-clock-rotate-left"></i> Gia Hạn Dịch Vụ

            </div>

            <form action="renew_service.php" method="GET" class="renew-form-modern"

                  onsubmit="return confirm('Xác nhận gia hạn gói này?');">

              <input type="hidden" name="csrf_token" value="<?= h($csrf_token) ?>">

              <input type="hidden" name="id" value="<?= (int)$service['id'] ?>">

              <div class="renew-content">

                <select name="period" class="renew-select" id="period<?= (int)$service['id'] ?>">

                  <option value="1">1 tháng</option>

                  <option value="3">3 tháng</option>

                  <option value="6">6 tháng</option>

                  <option value="8">8 tháng</option>

                  <option value="12">12 tháng</option>

                  <option value="18">18 tháng</option>

                  <option value="36">36 tháng</option>

                </select>

                <button type="submit" class="btn-action btn-renew">

                  <i class="fa fa-arrow-rotate-right"></i> Gia Hạn

                </button>

              </div>

            </form>

          </div>

        <?php endif; ?>

      </td>

    </tr>

    <?php

}

?>

<!DOCTYPE html>

<html lang="vi">

<head>

  <meta charset="UTF-8">

  <title>Quản Lý Dịch Vụ</title>

  <meta name="viewport" content="width=device-width, initial-scale=1">

  <link rel="icon" href="https://favicon.ico/iconvpnvietnam.png" type="image/x-icon">

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"/>

  <link rel="stylesheet" href="/css/manage_services.css">

  <link rel="stylesheet" href="/css/bootstrap/dashboard.css">

  <link rel="stylesheet" href="/css/manage_services_custom.min.css?v=<?= time() ?>">

  <script src="/js/manage_services.min.js?v=<?= time() ?>" defer></script>

</head>


<body>

<?php include_once __DIR__ . '/impersonation-bar.php'; ?>

<div class="dashboard-container">

    <nav class="sidebar">

        <div>

            <div class="sidebar-header">

                 <img src="<?= 'https://ui-avatars.com/api/?name=' . urlencode($_SESSION['username'] ?? 'User') ?>" alt="Avatar">

                <h2><?= h($_SESSION['username'] ?? 'User') ?></h2>

                <span><span class="status-dot"></span>Trực Tuyến</span>

            </div>

    <ul class="sidebar-menu">

      <li><a href="dashboard.php"><i class="fa fa-gauge"></i> Trang Chủ</a></li>

      <li><a href="deposit.php"><i class="fa fa-wallet"></i> Nạp Tiền</a></li>

      <li><a href="manage_services.php" class="active"><i class="fa fa-server"></i>Quản Lý Dịch Vụ</a></li>

      <li><a href="register_service.php"><i class="fa fa-plus-circle"></i>Đăng Ký Dịch Vụ</a></li>

      <li><a href="update_profile.php"><i class="fa fa-user"></i>Thông Tin Tài Khoản</a></li>

      <li><a href="support.php"><i class="fa fa-headset"></i>Trung Tâm Hỗ Trợ</a></li>

    </ul>

        </div>

       <div class="logout-btn">

            <a href="logout.php"><i class="fa fa-sign-out-alt"></i> Đăng Xuất</a>

        </div>

    </nav>

  <main class="main-content">

    <?php if ($msg === 'cancel_success'): ?>

      <div class="alert alert-success">Hủy gói dịch vụ thành công!</div>

    <?php elseif ($msg === 'success'): ?>

      <div class="alert alert-success">Mua gói dịch vụ thành công!</div>

    <?php elseif ($msg === 'renew_success'): ?>

      <div class="alert alert-success">Gia hạn gói dịch vụ thành công!</div>

    <?php elseif ($msg === 'renew_failed'): ?>

      <div class="alert alert-danger">Gia hạn không thành công, vui lòng kiểm tra số dư hoặc liên hệ hỗ trợ!</div>

    <?php endif; ?>



    <div class="section-title"><i class="fa fa-check-circle"></i> Dịch vụ đang sử dụng</div>

    <div class="table-responsive">

      <table class="service-table table">

        <thead>

          <tr>

            <th>Gói Dịch Vụ</th>

            <th>Server</th>

            <th>Thanh Toán</th>

            <th>Hạn Sử Dụng</th>

            <th>Trạng Thái</th>

            <th>QR Code Wireguard</th>

            <th>Public Key</th>

            <th>Cấu Hình Vless</th>

            <th>Thao Tác</th>

          </tr>

        </thead>

        <tbody>

        <?php if (count($active_services)): ?>

          <?php foreach ($active_services as $service) render_service_row($service, $qrCodeWebDir, $qrCodeDir, $vlessByService, $_SESSION['csrf_token']); ?>

        <?php else: ?>

          <tr><td colspan="9" class="empty-message">Bạn chưa có dịch vụ đang hoạt động.</td></tr>

        <?php endif; ?>

        </tbody>

      </table>

    </div>



    <div class="section-title"><i class="fa fa-clock"></i> Dịch vụ đã hết hạn</div>

    <div class="table-responsive">

      <table class="service-table table">

        <thead>

          <tr>

            <th>Gói Dịch Vụ</th>

            <th>Server</th>

            <th>Thanh Toán</th>

            <th>Hạn Sử Dụng</th>

            <th>Trạng Thái</th>

            <th>QR Code</th>

            <th>Public Key</th>

            <th>VLESS</th>

            <th>Thao Tác</th>

          </tr>

        </thead>

        <tbody>

        <?php if (count($expired_services)): ?>

          <?php foreach ($expired_services as $service) render_service_row($service, $qrCodeWebDir, $qrCodeDir, $vlessByService, $_SESSION['csrf_token']); ?>

        <?php else: ?>

          <tr><td colspan="9" class="empty-message">Không có dịch vụ hết hạn.</td></tr>

        <?php endif; ?>

        </tbody>

      </table>

    </div>



    <?php if (count($canceled_services)): ?>

      <div class="section-title" style="color:#c00;"><i class="fa fa-ban"></i> Dịch vụ đã hủy</div>

      <div class="table-responsive">

        <table class="service-table table">

          <thead>

            <tr>

              <th>Gói Dịch Vụ</th>

              <th>Server</th>

              <th>Thanh Toán</th>

              <th>Hạn Sử Dụng</th>

              <th>Trạng Thái</th>

              <th>QR Code</th>

              <th>Public Key</th>

              <th>VLESS</th>

              <th>Thao Tác</th>

            </tr>

          </thead>

          <tbody>

            <?php foreach ($canceled_services as $service) render_service_row($service, $qrCodeWebDir, $qrCodeDir, $vlessByService, $_SESSION['csrf_token']); ?>

          </tbody>

        </table>

      </div>

    <?php endif; ?>

  </main>

</div>

</body>

</html>
