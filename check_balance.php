<?php
/**
 * Kiểm tra số dư tài khoản (dùng cho AJAX auto-refresh)
 */
session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once 'db.php';

header('Content-Type: application/json; charset=utf-8');

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo json_encode(['success' => false, 'message' => 'Chưa đăng nhập']);
    exit();
}

$user_id = (int)$_SESSION['user_id'];

// Lấy số dư
$stmt = $conn->prepare("SELECT balance FROM users WHERE id = ? LIMIT 1");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$result = $stmt->get_result();
$user = $result->fetch_assoc();

if (!$user) {
    echo json_encode(['success' => false, 'message' => 'Không tìm thấy tài khoản']);
    exit();
}

echo json_encode([
    'success' => true,
    'balance' => (float)$user['balance']
]);
