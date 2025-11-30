<?php
/**
 * API kiểm tra trạng thái giao dịch
 * File này được gọi từ deposit.php để kiểm tra trạng thái giao dịch theo mã unique_code
 */

session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');
header('Content-Type: application/json; charset=utf-8');

require_once 'db.php';

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo json_encode([
        'success' => false,
        'message' => 'Not authenticated'
    ]);
    exit;
}

$user_id = (int)$_SESSION['user_id'];
$unique_code = $_GET['code'] ?? '';

if (empty($unique_code)) {
    echo json_encode([
        'success' => false,
        'message' => 'Missing transaction code'
    ]);
    exit;
}

try {
    // Lấy thông tin giao dịch
    $stmt = $conn->prepare("
        SELECT transaction_id, amount_paid, transaction_date, status, bank_transaction_ref, updated_at
        FROM transactions 
        WHERE user_id = ? AND unique_code = ? 
        LIMIT 1
    ");
    $stmt->bind_param("is", $user_id, $unique_code);
    $stmt->execute();
    $result = $stmt->get_result();
    $transaction = $result->fetch_assoc();
    
    if (!$transaction) {
        echo json_encode([
            'success' => false,
            'message' => 'Transaction not found'
        ]);
        exit;
    }
    
    // Trả về thông tin giao dịch
    echo json_encode([
        'success' => true,
        'transaction_id' => $transaction['transaction_id'],
        'amount' => number_format((float)$transaction['amount_paid'], 0, ',', '.'),
        'status' => $transaction['status'],
        'transaction_date' => date('d/m/Y H:i:s', strtotime($transaction['transaction_date'])),
        'updated_at' => $transaction['updated_at'] ? date('d/m/Y H:i:s', strtotime($transaction['updated_at'])) : null,
        'bank_ref' => $transaction['bank_transaction_ref'] ?? null
    ]);
    
} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'message' => 'Error: ' . $e->getMessage()
    ]);
}
