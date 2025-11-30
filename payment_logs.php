<?php
session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once 'db.php';

// Kiểm tra đăng nhập và quyền admin
if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit();
}

// Kiểm tra quyền admin (giả sử có cột role trong bảng users)
$user_id = (int)$_SESSION['user_id'];
$stmt = $conn->prepare("SELECT username, role FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$user = $stmt->get_result()->fetch_assoc();

if (!$user || ($user['role'] ?? '') !== 'admin') {
    die('Bạn không có quyền truy cập trang này!');
}

// Xử lý CSRF token
if (!isset($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

// Lọc dữ liệu
$filter_status = $_GET['status'] ?? 'all';
$filter_source = $_GET['source'] ?? 'all';
$filter_date = $_GET['date'] ?? date('Y-m-d');
$search_code = $_GET['search'] ?? '';

// Phân trang
$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$limit = 50;
$offset = ($page - 1) * $limit;

// Query logs
$where = ["1=1"];
$params = [];
$types = "";

if ($filter_status !== 'all') {
    $where[] = "status = ?";
    $params[] = $filter_status;
    $types .= "s";
}

if ($filter_source !== 'all') {
    $where[] = "source = ?";
    $params[] = $filter_source;
    $types .= "s";
}

if ($filter_date) {
    $where[] = "DATE(created_at) = ?";
    $params[] = $filter_date;
    $types .= "s";
}

if ($search_code) {
    $where[] = "(unique_code LIKE ? OR reference_number LIKE ? OR description LIKE ?)";
    $searchTerm = "%{$search_code}%";
    $params[] = $searchTerm;
    $params[] = $searchTerm;
    $params[] = $searchTerm;
    $types .= "sss";
}

$whereClause = implode(" AND ", $where);

// Đếm tổng số
$countSql = "SELECT COUNT(*) as total FROM payment_logs WHERE {$whereClause}";
$stmt = $conn->prepare($countSql);
if (!empty($params)) {
    $stmt->bind_param($types, ...$params);
}
$stmt->execute();
$totalRows = $stmt->get_result()->fetch_assoc()['total'];
$totalPages = ceil($totalRows / $limit);

// Lấy dữ liệu
$sql = "SELECT * FROM payment_logs WHERE {$whereClause} ORDER BY created_at DESC LIMIT ? OFFSET ?";
$params[] = $limit;
$params[] = $offset;
$types .= "ii";

$stmt = $conn->prepare($sql);
if (!empty($params)) {
    $stmt->bind_param($types, ...$params);
}
$stmt->execute();
$logs = $stmt->get_result();

// Thống kê
$statsSql = "SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed_count,
    SUM(CASE WHEN status='success' THEN amount ELSE 0 END) as total_amount,
    AVG(CASE WHEN status='success' THEN amount ELSE NULL END) as avg_amount
FROM payment_logs 
WHERE DATE(created_at) = ?";
$stmt = $conn->prepare($statsSql);
$stmt->bind_param("s", $filter_date);
$stmt->execute();
$stats = $stmt->get_result()->fetch_assoc();
?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Payment Logs - Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"/>
    <style>
        body { background: #f5f5f5; padding: 20px; }
        .stats-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-item { text-align: center; padding: 15px; }
        .stat-value { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 0.9em; margin-top: 5px; }
        .filter-bar { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .logs-table { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .badge-success-custom { background: #27ae60; color: white; }
        .badge-failed-custom { background: #e74c3c; color: white; }
        .badge-duplicate-custom { background: #95a5a6; color: white; }
        .raw-data { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; }
        .pagination { margin-top: 20px; }
    </style>
</head>
<body>
<div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2><i class="fa fa-chart-line"></i> Payment Logs - Quản Lý Thanh Toán Tự Động</h2>
        <div>
            <a href="dashboard.php" class="btn btn-secondary"><i class="fa fa-arrow-left"></i> Quay lại</a>
            <button class="btn btn-primary" onclick="location.reload()"><i class="fa fa-refresh"></i> Làm mới</button>
        </div>
    </div>

    <!-- Thống kê -->
    <div class="stats-card">
        <h5 class="mb-3"><i class="fa fa-chart-bar"></i> Thống kê ngày <?= htmlspecialchars($filter_date) ?></h5>
        <div class="row">
            <div class="col-md-3">
                <div class="stat-item">
                    <div class="stat-value"><?= number_format($stats['total_transactions']) ?></div>
                    <div class="stat-label">Tổng giao dịch</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-item">
                    <div class="stat-value text-success"><?= number_format($stats['success_count']) ?></div>
                    <div class="stat-label">Thành công</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-item">
                    <div class="stat-value text-danger"><?= number_format($stats['failed_count']) ?></div>
                    <div class="stat-label">Thất bại</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-item">
                    <div class="stat-value text-primary"><?= number_format($stats['total_amount'], 0, ',', '.') ?></div>
                    <div class="stat-label">Tổng tiền (VND)</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bộ lọc -->
    <div class="filter-bar">
        <form method="GET" class="row g-3">
            <div class="col-md-3">
                <label class="form-label">Ngày</label>
                <input type="date" name="date" class="form-control" value="<?= htmlspecialchars($filter_date) ?>">
            </div>
            <div class="col-md-2">
                <label class="form-label">Trạng thái</label>
                <select name="status" class="form-select">
                    <option value="all" <?= $filter_status === 'all' ? 'selected' : '' ?>>Tất cả</option>
                    <option value="success" <?= $filter_status === 'success' ? 'selected' : '' ?>>Thành công</option>
                    <option value="failed" <?= $filter_status === 'failed' ? 'selected' : '' ?>>Thất bại</option>
                    <option value="duplicate" <?= $filter_status === 'duplicate' ? 'selected' : '' ?>>Trùng lặp</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Nguồn</label>
                <select name="source" class="form-select">
                    <option value="all" <?= $filter_source === 'all' ? 'selected' : '' ?>>Tất cả</option>
                    <option value="casso" <?= $filter_source === 'casso' ? 'selected' : '' ?>>Casso</option>
                    <option value="payos" <?= $filter_source === 'payos' ? 'selected' : '' ?>>Payos</option>
                    <option value="bank" <?= $filter_source === 'bank' ? 'selected' : '' ?>>Bank</option>
                    <option value="generic" <?= $filter_source === 'generic' ? 'selected' : '' ?>>Generic</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Tìm kiếm</label>
                <input type="text" name="search" class="form-control" placeholder="Mã GD, nội dung..." value="<?= htmlspecialchars($search_code) ?>">
            </div>
            <div class="col-md-2">
                <label class="form-label">&nbsp;</label>
                <button type="submit" class="btn btn-primary w-100"><i class="fa fa-search"></i> Lọc</button>
            </div>
        </form>
    </div>

    <!-- Bảng logs -->
    <div class="logs-table">
        <h5 class="mb-3"><i class="fa fa-list"></i> Danh sách giao dịch (<?= number_format($totalRows) ?> kết quả)</h5>
        <div class="table-responsive">
            <table class="table table-hover table-bordered">
                <thead class="table-light">
                    <tr>
                        <th>ID</th>
                        <th>Transaction ID</th>
                        <th>User ID</th>
                        <th>Số tiền</th>
                        <th>Mã GD</th>
                        <th>Nội dung</th>
                        <th>Ref Number</th>
                        <th>Nguồn</th>
                        <th>Trạng thái</th>
                        <th>Thời gian</th>
                        <th>Raw Data</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if ($logs->num_rows > 0): ?>
                        <?php while ($log = $logs->fetch_assoc()): ?>
                            <tr>
                                <td><?= $log['id'] ?></td>
                                <td><?= $log['transaction_id'] ?? '-' ?></td>
                                <td><?= $log['user_id'] ?? '-' ?></td>
                                <td>
                                    <strong><?= number_format($log['amount'], 0, ',', '.') ?></strong>
                                    <?php if ($log['expected_amount'] && $log['amount'] != $log['expected_amount']): ?>
                                        <br><small class="text-muted">(Mong đợi: <?= number_format($log['expected_amount'], 0, ',', '.') ?>)</small>
                                    <?php endif; ?>
                                </td>
                                <td><?= htmlspecialchars($log['unique_code'] ?? '-') ?></td>
                                <td title="<?= htmlspecialchars($log['description'] ?? '') ?>">
                                    <?= htmlspecialchars(mb_substr($log['description'] ?? '', 0, 30)) ?>
                                    <?= mb_strlen($log['description'] ?? '') > 30 ? '...' : '' ?>
                                </td>
                                <td><?= htmlspecialchars($log['reference_number'] ?? '-') ?></td>
                                <td><span class="badge bg-info"><?= htmlspecialchars($log['source']) ?></span></td>
                                <td>
                                    <?php
                                    if ($log['status'] === 'success') {
                                        echo '<span class="badge badge-success-custom">Thành công</span>';
                                    } elseif ($log['status'] === 'failed') {
                                        echo '<span class="badge badge-failed-custom">Thất bại</span>';
                                    } else {
                                        echo '<span class="badge badge-duplicate-custom">' . htmlspecialchars($log['status']) . '</span>';
                                    }
                                    ?>
                                </td>
                                <td><?= date('H:i:s d/m/Y', strtotime($log['created_at'])) ?></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-secondary" 
                                            onclick="showRawData(<?= htmlspecialchars(json_encode($log['raw_data'])) ?>)">
                                        <i class="fa fa-eye"></i> Xem
                                    </button>
                                </td>
                            </tr>
                        <?php endwhile; ?>
                    <?php else: ?>
                        <tr><td colspan="11" class="text-center text-muted">Không có dữ liệu</td></tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

        <!-- Phân trang -->
        <?php if ($totalPages > 1): ?>
            <nav>
                <ul class="pagination justify-content-center">
                    <?php
                    $queryString = http_build_query(array_merge($_GET, ['page' => '']));
                    $queryString = rtrim($queryString, '=');
                    ?>
                    <li class="page-item <?= $page <= 1 ? 'disabled' : '' ?>">
                        <a class="page-link" href="?<?= $queryString ?>=<?= $page - 1 ?>">Trước</a>
                    </li>
                    <?php for ($i = max(1, $page - 2); $i <= min($totalPages, $page + 2); $i++): ?>
                        <li class="page-item <?= $i === $page ? 'active' : '' ?>">
                            <a class="page-link" href="?<?= $queryString ?>=<?= $i ?>"><?= $i ?></a>
                        </li>
                    <?php endfor; ?>
                    <li class="page-item <?= $page >= $totalPages ? 'disabled' : '' ?>">
                        <a class="page-link" href="?<?= $queryString ?>=<?= $page + 1 ?>">Sau</a>
                    </li>
                </ul>
            </nav>
        <?php endif; ?>
    </div>
</div>

<!-- Modal hiển thị raw data -->
<div class="modal fade" id="rawDataModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Raw Data</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <pre id="rawDataContent" style="background: #f5f5f5; padding: 15px; border-radius: 5px; max-height: 500px; overflow: auto;"></pre>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
function showRawData(data) {
    try {
        const formatted = JSON.stringify(JSON.parse(data), null, 2);
        document.getElementById('rawDataContent').textContent = formatted;
    } catch (e) {
        document.getElementById('rawDataContent').textContent = data || 'Không có dữ liệu';
    }
    new bootstrap.Modal(document.getElementById('rawDataModal')).show();
}
</script>
</body>
</html>
