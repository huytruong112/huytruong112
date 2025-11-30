<?php
/**
 * Check Transaction Status API
 * API để check trạng thái giao dịch (được gọi từ frontend)
 */

session_start();
date_default_timezone_set('Asia/Ho_Chi_Minh');

require_once 'db.php';
require_once 'auto_payment_check.php';
require_once 'payment_config.php';

// Set header JSON
header('Content-Type: application/json');

// Kiểm tra đăng nhập
if (!isset($_SESSION['user_id'])) {
    echo json_encode(['error' => 'Unauthorized', 'status' => null]);
    exit;
}

$user_id = (int)$_SESSION['user_id'];
$transaction_code = $_GET['code'] ?? '';

if (empty($transaction_code)) {
    echo json_encode(['error' => 'Missing transaction code', 'status' => null]);
    exit;
}

// Kiểm tra giao dịch thuộc về user này
$stmt = $conn->prepare("SELECT transaction_id, user_id, amount_paid, unique_code, status, transaction_date 
                        FROM transactions 
                        WHERE unique_code = ? AND user_id = ?");
$stmt->bind_param("si", $transaction_code, $user_id);
$stmt->execute();
$transaction = $stmt->get_result()->fetch_assoc();

if (!$transaction) {
    echo json_encode(['error' => 'Transaction not found', 'status' => null]);
    exit;
}

// Nếu đã success hoặc cancelled thì trả về luôn
if ($transaction['status'] === 'success' || $transaction['status'] === 'cancelled') {
    echo json_encode([
        'success' => true,
        'status' => $transaction['status'],
        'transaction_id' => $transaction['transaction_id'],
        'amount' => $transaction['amount_paid'],
        'date' => $transaction['transaction_date']
    ]);
    exit;
}

// Nếu vẫn pending - thử check auto với ngân hàng
if ($transaction['status'] === 'pending' && PAYMENT_AUTO_CHECK_ENABLED) {
    try {
        $processor = new AutoPaymentProcessor($conn);
        $result = $processor->checkSingleTransaction($transaction_code);
        
        // Lấy lại trạng thái mới nhất
        $stmt2 = $conn->prepare("SELECT status FROM transactions WHERE unique_code = ?");
        $stmt2->bind_param("s", $transaction_code);
        $stmt2->execute();
        $updated = $stmt2->get_result()->fetch_assoc();
        
        echo json_encode([
            'success' => true,
            'status' => $updated['status'] ?? 'pending',
            'transaction_id' => $transaction['transaction_id'],
            'amount' => $transaction['amount_paid'],
            'date' => $transaction['transaction_date'],
            'auto_check' => true,
            'message' => $result['message'] ?? ''
        ]);
        exit;
        
    } catch (Exception $e) {
        // Nếu có lỗi khi auto check, vẫn trả về status hiện tại
        echo json_encode([
            'success' => true,
            'status' => $transaction['status'],
            'transaction_id' => $transaction['transaction_id'],
            'amount' => $transaction['amount_paid'],
            'date' => $transaction['transaction_date'],
            'auto_check' => false,
            'error' => 'Auto check failed'
        ]);
        exit;
    }
}

// Trường hợp mặc định - trả về status hiện tại
echo json_encode([
    'success' => true,
    'status' => $transaction['status'],
    'transaction_id' => $transaction['transaction_id'],
    'amount' => $transaction['amount_paid'],
    'date' => $transaction['transaction_date']
]);

?>
