<?php
/**
 * API kiểm tra trạng thái giao dịch
 * Được gọi từ deposit.php để refresh trạng thái giao dịch
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
$code = $_GET['code'] ?? '';

if (empty($code)) {
    echo json_encode(['error' => 'No transaction code provided']);
    exit();
}

// Lấy trạng thái giao dịch
$stmt = $conn->prepare("
    SELECT status, amount_paid, transaction_date, updated_at 
    FROM transactions 
    WHERE user_id = ? AND unique_code = ? 
    LIMIT 1
");
$stmt->bind_param("is", $user_id, $code);
$stmt->execute();
$result = $stmt->get_result();
$transaction = $result->fetch_assoc();

if ($transaction) {
    echo json_encode([
        'success' => true,
        'status' => $transaction['status'],
        'amount' => (float)$transaction['amount_paid'],
        'created_at' => $transaction['transaction_date'],
        'updated_at' => $transaction['updated_at']
    ]);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'Transaction not found'
    ]);
}
