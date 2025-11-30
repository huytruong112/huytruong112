<?php
/**
 * API lấy chi tiết giao dịch
 * Được gọi từ deposit.php khi click "Xem chi tiết"
 */
session_start();
require_once 'db.php';

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo '<div class="text-danger">Vui lòng đăng nhập!</div>';
    exit();
}

$user_id = (int)$_SESSION['user_id'];
$transaction_id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($transaction_id <= 0) {
    echo '<div class="text-danger">Mã giao dịch không hợp lệ!</div>';
    exit();
}

// Lấy thông tin giao dịch
$stmt = $conn->prepare("
    SELECT t.*, u.username 
    FROM transactions t
    LEFT JOIN users u ON t.user_id = u.id
    WHERE t.transaction_id = ? AND t.user_id = ?
    LIMIT 1
");
$stmt->bind_param("ii", $transaction_id, $user_id);
$stmt->execute();
$tx = $stmt->get_result()->fetch_assoc();

if (!$tx) {
    echo '<div class="text-danger">Không tìm thấy giao dịch!</div>';
    exit();
}

// Lấy thông tin ngân hàng
$acc = $conn->query("SELECT bank_name, account_number, account_holder FROM receiving_accounts LIMIT 1");
$bank = $acc->fetch_assoc();

// Kiểm tra xem có log thanh toán tự động không
$stmt = $conn->prepare("
    SELECT * FROM payment_logs 
    WHERE transaction_id = ? 
    ORDER BY created_at DESC 
    LIMIT 1
");
$stmt->bind_param("i", $transaction_id);
$stmt->execute();
$paymentLog = $stmt->get_result()->fetch_assoc();
?>

<div class="container-fluid">
    <h6 class="mb-3"><strong>Thông tin giao dịch #<?= $tx['transaction_id'] ?></strong></h6>
    
    <table class="table table-bordered table-sm">
        <tr>
            <th width="40%">Mã giao dịch</th>
            <td><strong><?= htmlspecialchars($tx['unique_code']) ?></strong></td>
        </tr>
        <tr>
            <th>Số tiền</th>
            <td><strong class="text-primary"><?= number_format((float)$tx['amount_paid'], 0, ',', '.') ?> VND</strong></td>
        </tr>
        <tr>
            <th>Trạng thái</th>
            <td>
                <?php
                if ($tx['status'] == 'pending') {
                    echo '<span class="badge bg-warning">Chờ xử lý</span>';
                } elseif ($tx['status'] == 'success' || $tx['status'] == 'Thành công') {
                    echo '<span class="badge bg-success">Đã Thanh Toán</span>';
                } elseif ($tx['status'] == 'cancelled') {
                    echo '<span class="badge bg-danger">Đã hủy</span>';
                } else {
                    echo '<span class="badge bg-secondary">' . htmlspecialchars($tx['status']) . '</span>';
                }
                ?>
            </td>
        </tr>
        <tr>
            <th>Thời gian tạo</th>
            <td><?= date('H:i:s d/m/Y', strtotime($tx['transaction_date'])) ?></td>
        </tr>
        <?php if ($tx['updated_at']): ?>
        <tr>
            <th>Thời gian cập nhật</th>
            <td><?= date('H:i:s d/m/Y', strtotime($tx['updated_at'])) ?></td>
        </tr>
        <?php endif; ?>
        <tr>
            <th>Tài khoản</th>
            <td><?= htmlspecialchars($tx['username']) ?></td>
        </tr>
    </table>

    <?php if ($tx['status'] == 'pending'): ?>
        <div class="alert alert-info mb-3">
            <strong><i class="fa fa-info-circle"></i> Hướng dẫn thanh toán:</strong>
            <ol class="mb-0 mt-2">
                <li>Chuyển khoản: <strong><?= number_format((float)$tx['amount_paid'], 0, ',', '.') ?> VND</strong></li>
                <?php if ($bank): ?>
                <li>Ngân hàng: <strong><?= htmlspecialchars($bank['bank_name']) ?></strong></li>
                <li>Số TK: <strong><?= htmlspecialchars($bank['account_number']) ?></strong></li>
                <li>Chủ TK: <strong><?= htmlspecialchars($bank['account_holder']) ?></strong></li>
                <?php endif; ?>
                <li>Nội dung: <strong class="text-danger"><?= htmlspecialchars($tx['unique_code']) ?></strong></li>
            </ol>
            <p class="mb-0 mt-2 text-muted small">
                <i class="fa fa-clock"></i> Sau khi chuyển khoản, hệ thống sẽ tự động xác nhận trong vòng 2-5 phút.
            </p>
        </div>
    <?php endif; ?>

    <?php if ($paymentLog): ?>
        <hr>
        <h6><i class="fa fa-robot"></i> Thông tin thanh toán tự động</h6>
        <table class="table table-bordered table-sm">
            <tr>
                <th width="40%">Nguồn</th>
                <td><span class="badge bg-info"><?= strtoupper(htmlspecialchars($paymentLog['source'])) ?></span></td>
            </tr>
            <tr>
                <th>Số tiền nhận được</th>
                <td><?= number_format((float)$paymentLog['amount'], 0, ',', '.') ?> VND</td>
            </tr>
            <tr>
                <th>Mã tham chiếu</th>
                <td><?= htmlspecialchars($paymentLog['reference_number']) ?></td>
            </tr>
            <tr>
                <th>Nội dung CK</th>
                <td><?= htmlspecialchars($paymentLog['description']) ?></td>
            </tr>
            <tr>
                <th>Thời gian xử lý</th>
                <td><?= date('H:i:s d/m/Y', strtotime($paymentLog['created_at'])) ?></td>
            </tr>
            <tr>
                <th>Trạng thái</th>
                <td>
                    <?php
                    if ($paymentLog['status'] == 'success') {
                        echo '<span class="badge bg-success">Thành công</span>';
                    } else {
                        echo '<span class="badge bg-secondary">' . htmlspecialchars($paymentLog['status']) . '</span>';
                    }
                    ?>
                </td>
            </tr>
        </table>
        
        <div class="alert alert-success mb-0">
            <i class="fa fa-check-circle"></i> Giao dịch này đã được xử lý tự động bởi hệ thống thanh toán.
        </div>
    <?php elseif ($tx['status'] == 'success' || $tx['status'] == 'Thành công'): ?>
        <div class="alert alert-success mb-0">
            <i class="fa fa-check-circle"></i> Giao dịch đã được xác nhận và số dư đã được cộng vào tài khoản.
        </div>
    <?php elseif ($tx['status'] == 'cancelled'): ?>
        <div class="alert alert-danger mb-0">
            <i class="fa fa-times-circle"></i> Giao dịch đã bị hủy (quá thời gian thanh toán hoặc hủy bởi admin).
        </div>
    <?php endif; ?>
</div>

<style>
.table-bordered th {
    background-color: #f8f9fa;
    font-weight: 600;
}
.alert ol {
    padding-left: 20px;
}
</style>
