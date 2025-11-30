<?php
/**
 * Kiểm tra trạng thái giao dịch (dùng cho AJAX)
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
$code = $_GET['code'] ?? '';

if (empty($code)) {
    echo json_encode(['success' => false, 'message' => 'Thiếu mã giao dịch']);
    exit();
}

// Lấy thông tin giao dịch
$stmt = $conn->prepare(
    "SELECT transaction_id, amount_paid, status, transaction_date, unique_code 
     FROM transactions 
     WHERE user_id = ? AND unique_code = ? 
     LIMIT 1"
);
$stmt->bind_param("is", $user_id, $code);
$stmt->execute();
$result = $stmt->get_result();
$transaction = $result->fetch_assoc();

if (!$transaction) {
    echo json_encode(['success' => false, 'message' => 'Không tìm thấy giao dịch']);
    exit();
}

echo json_encode([
    'success' => true,
    'transaction_id' => $transaction['transaction_id'],
    'amount' => $transaction['amount_paid'],
    'status' => $transaction['status'],
    'date' => date('H:i:s d/m/Y', strtotime($transaction['transaction_date'])),
    'code' => $transaction['unique_code']
]);
