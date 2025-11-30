<?php
/**
 * API lấy chi tiết giao dịch
 * File này được gọi từ deposit.php để hiển thị chi tiết giao dịch trong modal
 */

session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');

require_once 'db.php';

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo '<div class="alert alert-danger">Bạn cần đăng nhập để xem thông tin này.</div>';
    exit;
}

$user_id = (int)$_SESSION['user_id'];
$transaction_id = (int)($_GET['id'] ?? 0);

if ($transaction_id <= 0) {
    echo '<div class="alert alert-danger">Mã giao dịch không hợp lệ.</div>';
    exit;
}

try {
    // Lấy thông tin giao dịch
    $stmt = $conn->prepare("
        SELECT t.*, u.username 
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        WHERE t.transaction_id = ? AND t.user_id = ?
        LIMIT 1
    ");
    $stmt->bind_param("ii", $transaction_id, $user_id);
    $stmt->execute();
    $result = $stmt->get_result();
    $transaction = $result->fetch_assoc();
    
    if (!$transaction) {
        echo '<div class="alert alert-danger">Không tìm thấy giao dịch hoặc bạn không có quyền xem.</div>';
        exit;
    }
    
    // Lấy log chi tiết từ payment_logs (nếu có)
    $stmt_log = $conn->prepare("
        SELECT * FROM payment_logs 
        WHERE transaction_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ");
    $stmt_log->bind_param("i", $transaction_id);
    $stmt_log->execute();
    $log_result = $stmt_log->get_result();
    $payment_log = $log_result->fetch_assoc();
    
    // Hiển thị thông tin
    ?>
    <div class="transaction-detail">
        <table class="table table-bordered">
            <tbody>
                <tr>
                    <th style="width: 40%;">Mã giao dịch:</th>
                    <td><strong><?= htmlspecialchars($transaction['transaction_id']) ?></strong></td>
                </tr>
                <tr>
                    <th>Tên tài khoản:</th>
                    <td><?= htmlspecialchars($transaction['username']) ?></td>
                </tr>
                <tr>
                    <th>Mã nội dung chuyển khoản:</th>
                    <td><code><?= htmlspecialchars($transaction['unique_code']) ?></code></td>
                </tr>
                <tr>
                    <th>Số tiền:</th>
                    <td>
                        <strong style="color: #28a745; font-size: 1.2em;">
                            <?= number_format((float)$transaction['amount_paid'], 0, ',', '.') ?> VND
                        </strong>
                    </td>
                </tr>
                <tr>
                    <th>Trạng thái:</th>
                    <td>
                        <?php
                        $status = $transaction['status'];
                        if ($status == 'pending') {
                            echo '<span class="badge bg-warning text-dark">Chờ xử lý</span>';
                        } elseif ($status == 'success' || $status == 'Thành công') {
                            echo '<span class="badge bg-success">Đã Thanh Toán</span>';
                        } elseif ($status == 'cancelled') {
                            echo '<span class="badge bg-danger">Đã Hủy</span>';
                        } else {
                            echo '<span class="badge bg-secondary">' . htmlspecialchars($status) . '</span>';
                        }
                        ?>
                    </td>
                </tr>
                <tr>
                    <th>Ngày tạo:</th>
                    <td><?= date('H:i:s d/m/Y', strtotime($transaction['transaction_date'])) ?></td>
                </tr>
                <?php if (!empty($transaction['updated_at'])): ?>
                <tr>
                    <th>Ngày cập nhật:</th>
                    <td><?= date('H:i:s d/m/Y', strtotime($transaction['updated_at'])) ?></td>
                </tr>
                <?php endif; ?>
                <?php if (!empty($transaction['bank_transaction_ref'])): ?>
                <tr>
                    <th>Mã tham chiếu ngân hàng:</th>
                    <td><code><?= htmlspecialchars($transaction['bank_transaction_ref']) ?></code></td>
                </tr>
                <?php endif; ?>
            </tbody>
        </table>
        
        <?php if ($payment_log): ?>
        <hr>
        <h6><i class="fa fa-info-circle"></i> Chi tiết thanh toán</h6>
        <table class="table table-bordered table-sm">
            <tbody>
                <?php if (!empty($payment_log['bank_transaction_ref'])): ?>
                <tr>
                    <th style="width: 40%;">Mã giao dịch ngân hàng:</th>
                    <td><code><?= htmlspecialchars($payment_log['bank_transaction_ref']) ?></code></td>
                </tr>
                <?php endif; ?>
                <tr>
                    <th>Thời gian xử lý:</th>
                    <td><?= date('H:i:s d/m/Y', strtotime($payment_log['created_at'])) ?></td>
                </tr>
                <?php 
                if (!empty($payment_log['extra_data'])) {
                    $extra_data = json_decode($payment_log['extra_data'], true);
                    if ($extra_data && is_array($extra_data)):
                ?>
                <tr>
                    <th>Thông tin bổ sung:</th>
                    <td>
                        <ul class="mb-0" style="font-size: 0.9em;">
                            <?php if (isset($extra_data['bank']) || isset($extra_data['bank_name'])): ?>
                            <li><strong>Ngân hàng:</strong> <?= htmlspecialchars($extra_data['bank'] ?? $extra_data['bank_name'] ?? 'N/A') ?></li>
                            <?php endif; ?>
                            <?php if (isset($extra_data['transaction_date'])): ?>
                            <li><strong>Ngày GD:</strong> <?= htmlspecialchars($extra_data['transaction_date']) ?></li>
                            <?php endif; ?>
                            <?php if (isset($extra_data['description'])): ?>
                            <li><strong>Nội dung:</strong> <?= htmlspecialchars($extra_data['description']) ?></li>
                            <?php endif; ?>
                            <?php if (isset($extra_data['payment_method'])): ?>
                            <li><strong>Phương thức:</strong> <?= htmlspecialchars($extra_data['payment_method']) ?></li>
                            <?php endif; ?>
                        </ul>
                    </td>
                </tr>
                <?php 
                    endif;
                } 
                ?>
            </tbody>
        </table>
        <?php endif; ?>
        
        <?php if ($status == 'pending'): ?>
        <div class="alert alert-info mt-3">
            <i class="fa fa-info-circle"></i> 
            <strong>Lưu ý:</strong> Giao dịch đang chờ xử lý. Vui lòng chuyển khoản với nội dung 
            <strong><?= htmlspecialchars($transaction['unique_code']) ?></strong> 
            để hệ thống tự động xác nhận.
        </div>
        <?php endif; ?>
        
        <?php if ($status == 'success' || $status == 'Thành công'): ?>
        <div class="alert alert-success mt-3">
            <i class="fa fa-check-circle"></i> 
            <strong>Thành công!</strong> Giao dịch đã được xác nhận và số tiền đã được cộng vào tài khoản của bạn.
        </div>
        <?php endif; ?>
        
        <?php if ($status == 'cancelled'): ?>
        <div class="alert alert-danger mt-3">
            <i class="fa fa-times-circle"></i> 
            <strong>Đã hủy:</strong> Giao dịch này đã bị hủy. Nếu bạn đã chuyển khoản, vui lòng liên hệ hỗ trợ.
        </div>
        <?php endif; ?>
    </div>
    
    <?php
    
} catch (Exception $e) {
    echo '<div class="alert alert-danger">Lỗi: ' . htmlspecialchars($e->getMessage()) . '</div>';
}
