<?php
/**
 * API kiểm tra số dư tài khoản
 * Được gọi từ deposit.php để refresh số dư realtime
 */
session_start();
header('Content-Type: application/json; charset=utf-8');

require_once 'db.php';

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo json_encode(['error' => 'Not logged in']);
    exit();
}

$user_id = (int)$_SESSION['user_id'];

// Lấy số dư hiện tại
$stmt = $conn->prepare("SELECT balance FROM users WHERE id = ?");
$stmt->bind_param("i", $user_id);
$stmt->execute();
$result = $stmt->get_result();
$user = $result->fetch_assoc();

if ($user) {
    echo json_encode([
        'success' => true,
        'balance' => (float)$user['balance']
    ]);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'User not found'
    ]);
}
