<?php
/**
 * Check Balance API
 * API để kiểm tra số dư user (được gọi từ frontend)
 */

session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');

require_once 'db.php';

// Set header JSON
header('Content-Type: application/json');

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo json_encode(['error' => 'Unauthorized', 'balance' => 0]);
    exit;
}

$user_id = (int)$_SESSION['user_id'];

// Lấy số dư hiện tại
$stmt = $conn->prepare("SELECT balance FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$user = $stmt->get_result()->fetch_assoc();

if (!$user) {
    echo json_encode(['error' => 'User not found', 'balance' => 0]);
    exit;
}

echo json_encode([
    'success' => true,
    'balance' => floatval($user['balance'] ?? 0)
]);

?>
