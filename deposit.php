<?php
session_start();
// Thiết lập múi giờ chuẩn Việt Nam ngay đầu file
date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once 'db.php';

// Redirect if not logged in
if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit();
}
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (
        !isset($_POST['csrf_token']) ||
        !hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'])
    ) {
        die('CSRF validation failed');
    }
}
$user_id = (int)$_SESSION['user_id'];

// Lấy thông tin user
$stmt = $conn->prepare("SELECT username, balance FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$user = $stmt->get_result()->fetch_assoc();

// Lấy tài khoản ngân hàng chính
$acc = $conn->query("SELECT bank_name, account_number, account_holder, branch FROM receiving_accounts LIMIT 1");
$main_account = $acc->fetch_assoc();

// Lấy giao dịch pending nếu có code
$show_instructions = false;
$transaction_code = $_GET['code'] ?? '';
$pending_tx = null;
$pending_status = null;
if ($transaction_code) {
    $stmt_ck = $conn->prepare("SELECT amount_paid, unique_code, status FROM transactions WHERE user_id=? AND unique_code=? LIMIT 1");
    $stmt_ck->bind_param("is", $user_id, $transaction_code);
    $stmt_ck->execute();
    $pending_tx = $stmt_ck->get_result()->fetch_assoc();
    if ($pending_tx) {
        $show_instructions = true;
        $pending_status = $pending_tx['status'];
    }
}

// Xử lý submit nạp tiền
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['amount'])) {
    $amount = (int)$_POST['amount'];
    if ($amount > 0 && $amount <= 50000000) {
        $code = 'TS' . str_pad(rand(0, 99999), 5, '0', STR_PAD_LEFT);
        // NOW() trong SQL sẽ lấy giờ hệ thống (đã chỉnh ở bước trước)
        $stmt2 = $conn->prepare("INSERT INTO transactions (user_id, amount_paid, transaction_date, status, unique_code) VALUES (?, ?, NOW(), 'pending', ?)");
        $stmt2->bind_param("ids", $user_id, $amount, $code);
        $stmt2->execute();
        header("Location: pay.php?code={$code}");
        exit();
    } else {
        $_SESSION['message'] = "Số tiền nạp không hợp lệ (tối đa 50 triệu/lần)!";
        header('Location: deposit.php');
        exit();
    }
}

// Lịch sử nạp tiền
$stmt = $conn->prepare("SELECT transaction_id, amount_paid, transaction_date, unique_code, status FROM transactions WHERE user_id=? AND amount_paid>0 ORDER BY transaction_date DESC");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$history = $stmt->get_result();

// Lịch sử mua gói
$stmt2 = $conn->prepare("SELECT us.id AS service_id, sp.package_name, us.server, us.payment_date, us.status FROM user_services us JOIN service_packages sp ON us.package_id = sp.id WHERE us.user_id = ? ORDER BY us.payment_date DESC");
$stmt2->bind_param("i", $user_id);
$stmt2->execute();
$purchases = $stmt2->get_result();
?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Nạp Tiền - VPN Việt Nam</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <link rel="icon" href="favicon.ico/iconvpnvietnam.png">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"/>
    <link rel="stylesheet" href="/css/bootstrap/deposit.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="/css/bootstrap/dashboard.css">
    <script src="/js/deposit.min.js?v=<?= time() ?>" defer></script>
</head>
<body>
<div class="dashboard-container">
    <nav class="sidebar">
        <div>
            <div class="sidebar-header">
                <img src="<?= htmlspecialchars($user['avatar'] ?? 'https://ui-avatars.com/api/?name=' . urlencode($user['username'] ?? 'User')) ?>" alt="Avatar">
                <h2><?= htmlspecialchars($user['username'] ?? 'User') ?></h2>
                <span><span class="status-dot"></span>Trực Tuyến</span>
            </div>
    <ul class="sidebar-menu">
      <li><a href="dashboard"><i class="fa fa-gauge"></i> Trang Chủ</a></li>
      <li><a href="deposit" class="active"><i class="fa fa-wallet"></i> Nạp Tiền</a></li>
      <li><a href="manage_services" class=""><i class="fa fa-server"></i>Quản Lý Dịch Vụ</a></li>
      <li><a href="register_service"><i class="fa fa-plus-circle"></i> Đăng Ký Dịch Vụ</a></li>
      <li><a href="update_profile"><i class="fa fa-user"></i>Thông Tin Cá Nhân</a></li>
      <li><a href="support.php"><i class="fa fa-headset"></i>Trung Tâm Hỗ Trợ</a></li>
    </ul>
        </div>
       <div class="logout-btn">
            <a href="logout.php"><i class="fa fa-sign-out-alt"></i> Đăng Xuất</a>
        </div>
    </nav>
    <main class="main-content">
        <?php if (isset($_SESSION['message'])): ?>
            <div class="alert"><?= htmlspecialchars($_SESSION['message']) ?></div>
            <?php unset($_SESSION['message']); ?>
        <?php endif; ?>

        <div class="balance-card section mb-4">
            <div class="balance-card-icon">
                <i class="fa-solid fa-wallet"></i>
            </div>
            <div class="balance-card-info">
                <div class="balance-label">Số dư hiện tại</div>
                <div class="balance-value" id="userBalance">
    <?= number_format((float)($user['balance'] ?? 0), 0, ',', '.') ?>
    <span class="balance-unit">VND</span>
</div>
            </div>
        </div>

        <div class="section" id="deposit">
            <h3><i class="fa-solid fa-circle-plus"></i> Nạp Tiền</h3>
      <form action="deposit.php" method="POST" autocomplete="off">
    <input type="hidden" name="csrf_token" value="<?= $_SESSION['csrf_token'] ?>">
    <label for="amount" class="form-label">Số Tiền (VND):</label>
    <input type="number" name="amount" id="amount" required min="10000" placeholder="Nhập số tiền muốn nạp" />
    <P>Số tiền nạp tối thiểu 10.000 VNĐ, và tối đa 50.000.000 VND</P>
    <button type="submit" class="btn-deposit"><i class="fa fa-arrow-right"></i> Nạp Tiền</button>
</form>
        </div>
        <?php if ($show_instructions && $pending_tx): ?>
            <div class="section" style="margin-top:20px;">
                <h3><i class="fa-solid fa-credit-card"></i> Hướng Dẫn Chuyển Khoản</h3>
                <p>
                    Bạn đã yêu cầu nạp <strong><?= number_format((float)($pending_tx['amount_paid'] ?? 0), 0, ',', '.') ?> VND</strong>.<br/>
                    Vui lòng chuyển khoản theo thông tin bên dưới:
                </p>
                <ul>
                  <?php if ($main_account): ?>
                    <li><strong>Ngân hàng:</strong> <?= htmlspecialchars($main_account['bank_name']) ?></li>
                    <li><strong>Số tài khoản:</strong> <?= htmlspecialchars($main_account['account_number']) ?></li>
                    <li><strong>Tên chủ Tài khoản:</strong> <?= htmlspecialchars($main_account['account_holder']) ?></li>
                    <?php if (!empty($main_account['branch'])): ?>
                      <li><strong>Chi nhánh:</strong> <?= htmlspecialchars($main_account['branch']) ?></li>
                    <?php endif; ?>
                  <?php else: ?>
                    <li><strong>Ngân hàng:</strong></li>
                    <li><strong>Số tài khoản:</strong></li>
                    <li><strong>Tên chủ TK:</strong></li>
                  <?php endif; ?>
                  <li><strong>Nội dung chuyển khoản:</strong> <?= htmlspecialchars($pending_tx['unique_code']) ?></li>
                </ul>
                <p style="color:red;">
                    <a href="support" class="support">Hỗ Trợ Khách Hàng</a>)
                </p>
                <p style="color:red;">
                    Vui lòng ghi đúng nội dung chuyển khoản để xác nhận nhanh. Lệnh nạp tiền sẽ được xác nhận trong 2 phút, nếu chưa thanh toán sau 24h sẽ bị huỷ.
                </p>
                <p>
                    Sau khi chuyển khoản, chúng tôi sẽ kiểm tra và cập nhật số dư của bạn.<br/>
                    Liên hệ: <strong>Hotline : 0812.363.898</strong> hoặc <a href="support" class="support">Hỗ Trợ Khách Hàng</a>.
                </p>
                <hr>
                <div>
                    <strong>Trạng thái giao dịch:</strong>
                    <span id="transaction-status">
                        <?php
                        if ($pending_status == 'pending') {
                            echo '<span class="badge text-bg-warning">Chờ xử lý</span>';
                        } elseif ($pending_status == 'success' || $pending_status == 'Thành công') {
                            echo '<span class="badge text-bg-success">Đã Thanh Toán</span>';
                        } elseif ($pending_status) {
                            echo '<span class="badge text-bg-secondary">'.htmlspecialchars($pending_status).'</span>';
                        } else {
                            echo '<span class="badge text-bg-secondary">Không rõ</span>';
                        }
                        ?>
                    </span>
                    <button type="button" class="btn btn-sm btn-outline-primary ms-2" id="btn-refresh-status">
                        <i class="fa fa-refresh"></i> Xem lại trạng thái
                    </button>
                </div>
            </div>
        <?php endif; ?>

        <div class="section" id="transactions">
            <h3><i class="fa-solid fa-clock-rotate-left"></i> Lịch Sử Giao Dịch Nạp Tiền</h3>
            <div class="table-responsive">
            <table class="table table-bordered align-middle">
                <thead class="table-light">
                    <tr>
                        <th>Mã GD</th>
                        <th>Số Tiền</th>
                        <th>Ngày Tạo</th>
                        <th>Nội Dung</th>
                        <th>Trạng Thái</th>
                        <th>Chi tiết</th>
                    </tr>
                </thead>
                <tbody>
                <?php if ($history->num_rows > 0): ?>
                    <?php while ($row = $history->fetch_assoc()): ?>
                        <tr>
                            <td><?= $row['transaction_id'] ?></td>
                            <td><?= number_format((float)($row['amount_paid'] ?? 0), 0, ',', '.') ?> VND</td>
                            <td><?= date('H:i:s d/m/Y', strtotime($row['transaction_date'])) ?></td>
                            <td><?= htmlspecialchars($row['unique_code'] ?? '') ?></td>
                            <td>
                                <?php
                                if ($row['status'] == 'pending') {
                                    echo '<span class="badge text-bg-warning">Chờ xử lý</span>';
                                } elseif ($row['status'] == 'success' || $row['status'] == 'Thành công') {
                                    echo '<span class="badge text-bg-success">Đã Thanh Toán</span>';
                                } else {
                                    echo '<span class="badge text-bg-secondary">'.htmlspecialchars($row['status']).'</span>';
                                }
                                ?>
                            </td>
                            <td>
                                <button class="btn btn-info btn-sm btn-detail-transaction" 
                                        data-transaction-id="<?= $row['transaction_id'] ?>"
                                        data-unique-code="<?= htmlspecialchars($row['unique_code']) ?>">
                                    <i class="fa fa-eye"></i> Xem chi tiết
                                </button>
                            </td>
                        </tr>
                    <?php endwhile; ?>
                <?php else: ?>
                    <tr><td colspan='6'>Chưa có giao dịch nạp tiền nào.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
            </div>
        </div>

        <div class="modal fade" id="transactionDetailModal" tabindex="-1" aria-labelledby="transactionDetailModalLabel" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="transactionDetailModalLabel"><i class="fa fa-receipt"></i> Chi tiết giao dịch</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Đóng"></button>
              </div>
              <div class="modal-body" id="transaction-detail-modal-content">
                <div class="text-center text-secondary">Đang tải...</div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
              </div>
            </div>
          </div>
        </div>
        <div class="section" id="purchases">
            <h3><i class="fa-solid fa-layer-group"></i> Lịch Sử Mua Gói</h3>
            <div class="table-responsive">
            <table class="table table-bordered align-middle">
                <thead class="table-light">
                    <tr>
                        <th>ID Dịch Vụ</th>
                        <th>Gói</th>
                        <th>Server</th>
                        <th>Ngày Mua</th>
                        <th>Trạng Thái</th>
                    </tr>
                </thead>
                <tbody>
                <?php if ($purchases->num_rows > 0): ?>
                    <?php while ($p = $purchases->fetch_assoc()): ?>
                        <tr>
                            <td><?= $p['service_id'] ?></td>
                            <td><?= htmlspecialchars($p['package_name']) ?></td>
                            <td><?= htmlspecialchars($p['server']) ?></td>
                            <td><?= date('H:i:s d/m/Y', strtotime($p['payment_date'])) ?></td>
                            <td>
                                <?php
                                if ($p['status'] == 'active') {
                                    echo '<span class="badge text-bg-success">Đang dùng</span>';
                                } elseif ($p['status'] == 'expired') {
                                    echo '<span class="badge text-bg-danger">Hết hạn</span>';
                                } else {
                                    echo '<span class="badge text-bg-secondary">'.htmlspecialchars($p['status']).'</span>';
                                }
                                ?>
                            </td>
                        </tr>
                    <?php endwhile; ?>
                <?php else: ?>
                    <tr><td colspan='5'>Bạn chưa mua gói dịch vụ nào.</td></tr>
                <?php endif; ?>
                </tbody>
            </table>
            </div>
        </div>
    </main>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
