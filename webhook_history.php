<?php
/**
 * Xem lịch sử webhook (admin only)
 * Hiển thị các request webhook đã nhận
 */
session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once 'db.php';

// Kiểm tra quyền admin (thay đổi logic này theo hệ thống của bạn)
if (!isset($_SESSION['user_id']) || !isset($_SESSION['is_admin']) || !$_SESSION['is_admin']) {
    die('Access denied. Admin only.');
}

$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$limit = 50;
$offset = ($page - 1) * $limit;

// Lấy tổng số
$total = $conn->query("SELECT COUNT(*) as count FROM webhook_logs")->fetch_assoc()['count'];
$total_pages = ceil($total / $limit);

// Lấy logs
$stmt = $conn->prepare("
    SELECT id, payload, response, status_code, ip_address, processed, error_message, created_at
    FROM webhook_logs
    ORDER BY created_at DESC
    LIMIT ? OFFSET ?
");
$stmt->bind_param("ii", $limit, $offset);
$stmt->execute();
$logs = $stmt->get_result();
?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Webhook History - Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .log-payload { 
            max-height: 100px; 
            overflow-y: auto; 
            font-size: 12px;
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
        }
        .badge-processed { background-color: #28a745; }
        .badge-pending { background-color: #ffc107; }
        .badge-error { background-color: #dc3545; }
    </style>
</head>
<body>
<div class="container my-5">
    <h1>📊 Webhook History</h1>
    <p class="text-muted">Tổng: <?= $total ?> requests | Trang <?= $page ?>/<?= $total_pages ?></p>
    
    <div class="table-responsive">
        <table class="table table-bordered table-hover">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>IP</th>
                    <th>Payload</th>
                    <th>Response</th>
                    <th>Status</th>
                    <th>Processed</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
            <?php if ($logs->num_rows > 0): ?>
                <?php while ($log = $logs->fetch_assoc()): ?>
                <tr>
                    <td><?= $log['id'] ?></td>
                    <td><?= htmlspecialchars($log['ip_address']) ?></td>
                    <td>
                        <div class="log-payload">
                            <pre><?= htmlspecialchars($log['payload']) ?></pre>
                        </div>
                    </td>
                    <td>
                        <div class="log-payload">
                            <pre><?= htmlspecialchars($log['response']) ?></pre>
                        </div>
                    </td>
                    <td>
                        <span class="badge bg-<?= $log['status_code'] >= 200 && $log['status_code'] < 300 ? 'success' : 'danger' ?>">
                            <?= $log['status_code'] ?>
                        </span>
                    </td>
                    <td>
                        <?php if ($log['processed']): ?>
                            <span class="badge badge-processed">✓ Yes</span>
                        <?php else: ?>
                            <span class="badge badge-pending">⏳ No</span>
                        <?php endif; ?>
                        <?php if ($log['error_message']): ?>
                            <br><small class="text-danger"><?= htmlspecialchars($log['error_message']) ?></small>
                        <?php endif; ?>
                    </td>
                    <td><?= date('H:i:s d/m/Y', strtotime($log['created_at'])) ?></td>
                </tr>
                <?php endwhile; ?>
            <?php else: ?>
                <tr><td colspan="7" class="text-center">Chưa có log nào</td></tr>
            <?php endif; ?>
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    <?php if ($total_pages > 1): ?>
    <nav>
        <ul class="pagination justify-content-center">
            <?php if ($page > 1): ?>
            <li class="page-item"><a class="page-link" href="?page=<?= $page - 1 ?>">« Prev</a></li>
            <?php endif; ?>
            
            <?php for ($i = max(1, $page - 5); $i <= min($total_pages, $page + 5); $i++): ?>
            <li class="page-item <?= $i == $page ? 'active' : '' ?>">
                <a class="page-link" href="?page=<?= $i ?>"><?= $i ?></a>
            </li>
            <?php endfor; ?>
            
            <?php if ($page < $total_pages): ?>
            <li class="page-item"><a class="page-link" href="?page=<?= $page + 1 ?>">Next »</a></li>
            <?php endif; ?>
        </ul>
    </nav>
    <?php endif; ?>
    
    <div class="mt-4">
        <a href="dashboard.php" class="btn btn-secondary">← Back to Dashboard</a>
        <a href="?clear=1" class="btn btn-danger" onclick="return confirm('Xóa tất cả logs?')">🗑️ Clear All Logs</a>
    </div>
</div>

<?php
// Xử lý clear logs
if (isset($_GET['clear']) && $_GET['clear'] == 1) {
    $conn->query("TRUNCATE TABLE webhook_logs");
    header('Location: webhook_history.php');
    exit();
}
?>
</body>
</html>
