<?php
/**
 * Transaction Detail
 * Hiển thị chi tiết giao dịch (được gọi từ modal)
 */

session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');

require_once 'db.php';

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo '<div class="text-danger">Bạn cần đăng nhập!</div>';
    exit;
}

$user_id = (int)$_SESSION['user_id'];
$transaction_id = (int)($_GET['id'] ?? 0);

if ($transaction_id <= 0) {
    echo '<div class="text-danger">ID giao dịch không hợp lệ!</div>';
    exit;
}

// Lấy thông tin giao dịch
$stmt = $conn->prepare("SELECT t.*, u.username 
                        FROM transactions t 
                        JOIN users u ON t.user_id = u.id 
                        WHERE t.transaction_id = ? AND t.user_id = ?");
$stmt->bind_param("ii", $transaction_id, $user_id);
$stmt->execute();
$tx = $stmt->get_result()->fetch_assoc();

if (!$tx) {
    echo '<div class="text-danger">Không tìm thấy giao dịch!</div>';
    exit;
}

// Lấy thông tin tài khoản ngân hàng
$acc = $conn->query("SELECT bank_name, account_number, account_holder, branch FROM receiving_accounts LIMIT 1");
$bank = $acc->fetch_assoc();

?>

<div class="transaction-detail">
    <div class="row mb-3">
        <div class="col-5 text-muted">Mã giao dịch:</div>
        <div class="col-7"><strong><?= htmlspecialchars($tx['unique_code']) ?></strong></div>
    </div>
    
    <div class="row mb-3">
        <div class="col-5 text-muted">Số tiền:</div>
        <div class="col-7">
            <strong class="text-success"><?= number_format((float)$tx['amount_paid'], 0, ',', '.') ?> VND</strong>
        </div>
    </div>
    
    <div class="row mb-3">
        <div class="col-5 text-muted">Ngày tạo:</div>
        <div class="col-7"><?= date('H:i:s d/m/Y', strtotime($tx['transaction_date'])) ?></div>
    </div>
    
    <div class="row mb-3">
        <div class="col-5 text-muted">Trạng thái:</div>
        <div class="col-7">
            <?php
            if ($tx['status'] == 'pending') {
                echo '<span class="badge text-bg-warning">Chờ xử lý</span>';
            } elseif ($tx['status'] == 'success' || $tx['status'] == 'Thành công') {
                echo '<span class="badge text-bg-success">Đã Thanh Toán</span>';
            } elseif ($tx['status'] == 'cancelled') {
                echo '<span class="badge text-bg-danger">Đã hủy</span>';
            } else {
                echo '<span class="badge text-bg-secondary">'.htmlspecialchars($tx['status']).'</span>';
            }
            ?>
        </div>
    </div>

    <?php if ($tx['status'] == 'pending'): ?>
        <hr>
        <h6><i class="fa fa-info-circle"></i> Thông tin chuyển khoản</h6>
        
        <?php if ($bank): ?>
            <div class="alert alert-info">
                <div class="mb-2"><strong>Ngân hàng:</strong> <?= htmlspecialchars($bank['bank_name']) ?></div>
                <div class="mb-2"><strong>Số TK:</strong> <?= htmlspecialchars($bank['account_number']) ?></div>
                <div class="mb-2"><strong>Chủ TK:</strong> <?= htmlspecialchars($bank['account_holder']) ?></div>
                <?php if (!empty($bank['branch'])): ?>
                    <div class="mb-2"><strong>Chi nhánh:</strong> <?= htmlspecialchars($bank['branch']) ?></div>
                <?php endif; ?>
                <div class="mt-3 p-2 bg-warning text-dark rounded">
                    <strong>Nội dung CK:</strong> <span class="text-danger fw-bold"><?= htmlspecialchars($tx['unique_code']) ?></span>
                </div>
            </div>
        <?php endif; ?>
        
        <div class="text-muted small mt-2">
            <i class="fa fa-clock"></i> Giao dịch sẽ tự động được xác nhận khi bạn chuyển khoản với đúng nội dung.
        </div>
    <?php endif; ?>

    <?php if ($tx['status'] == 'success' && !empty($tx['updated_at'])): ?>
        <div class="row mb-3">
            <div class="col-5 text-muted">Xác nhận lúc:</div>
            <div class="col-7"><?= date('H:i:s d/m/Y', strtotime($tx['updated_at'])) ?></div>
        </div>
    <?php endif; ?>
</div>

<style>
.transaction-detail .row {
    font-size: 0.95rem;
}
.transaction-detail .alert {
    font-size: 0.9rem;
}
</style>
