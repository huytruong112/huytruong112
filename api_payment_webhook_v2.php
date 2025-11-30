<?php
/**
 * API Webhook v2 - Có log vào database
 * Version nâng cao với logging vào DB để theo dõi
 */

date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once __DIR__ . '/config_payment.php';
require_once __DIR__ . '/db.php';

header('Content-Type: application/json; charset=utf-8');

/**
 * Log vào file
 */
function webhook_log(string $message, string $level = 'INFO'): void {
    $logFile = WEBHOOK_LOG_FILE;
    $logDir = dirname($logFile);
    if (!is_dir($logDir)) @mkdir($logDir, 0755, true);
    $timestamp = date('Y-m-d H:i:s');
    $logMessage = "[{$timestamp}] [{$level}] {$message}\n";
    @file_put_contents($logFile, $logMessage, FILE_APPEND | LOCK_EX);
}

/**
 * Log vào database
 */
function webhook_log_db(mysqli $conn, array $payload, array $response, int $status_code, bool $processed, ?string $error = null): void {
    try {
        $payload_json = json_encode($payload, JSON_UNESCAPED_UNICODE);
        $response_json = json_encode($response, JSON_UNESCAPED_UNICODE);
        $ip = $_SERVER['REMOTE_ADDR'] ?? '';
        
        $stmt = $conn->prepare("
            INSERT INTO webhook_logs (payload, response, status_code, ip_address, processed, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, NOW())
        ");
        $stmt->bind_param("ssiiss", $payload_json, $response_json, $status_code, $ip, $processed, $error);
        $stmt->execute();
    } catch (Exception $e) {
        webhook_log("Failed to log to DB: " . $e->getMessage(), 'ERROR');
    }
}

/**
 * Response JSON và exit
 */
function json_response(array $data, int $status = 200): void {
    global $conn, $initial_payload;
    
    // Log vào DB trước khi exit
    if (isset($conn) && isset($initial_payload)) {
        $processed = ($status >= 200 && $status < 300 && ($data['success'] ?? false));
        $error = $processed ? null : ($data['message'] ?? 'Unknown error');
        webhook_log_db($conn, $initial_payload, $data, $status, $processed, $error);
    }
    
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit();
}

/**
 * Kiểm tra IP whitelist
 */
function check_ip_whitelist(): bool {
    if (!CHECK_IP_WHITELIST) return true;
    $client_ip = $_SERVER['REMOTE_ADDR'] ?? '';
    if (in_array($client_ip, ALLOWED_IPS, true)) return true;
    webhook_log("Blocked IP: {$client_ip}", 'WARNING');
    return false;
}

/**
 * Tìm unique_code
 */
function extract_unique_code(string $content): ?string {
    $normalized = strtoupper(trim($content));
    if (preg_match('/TS[\s\-]?(\d{5})/', $normalized, $matches)) {
        return 'TS' . $matches[1];
    }
    return null;
}

/**
 * Xử lý payment
 */
function process_payment(mysqli $conn, array $data): array {
    $amount = (float)($data['amount'] ?? 0);
    $content = trim($data['description'] ?? $data['content'] ?? '');
    $bank_transaction_id = $data['transaction_id'] ?? $data['id'] ?? '';
    
    if ($amount <= 0) {
        return ['success' => false, 'message' => 'Số tiền không hợp lệ'];
    }
    
    if (empty($content)) {
        return ['success' => false, 'message' => 'Thiếu nội dung chuyển khoản'];
    }
    
    $unique_code = extract_unique_code($content);
    if (!$unique_code) {
        webhook_log("Cannot extract unique_code from: {$content}", 'WARNING');
        return ['success' => false, 'message' => 'Không tìm thấy mã giao dịch trong nội dung'];
    }
    
    $conn->begin_transaction();
    
    try {
        // Tìm transaction pending
        $stmt = $conn->prepare("
            SELECT transaction_id, user_id, amount_paid, status 
            FROM transactions 
            WHERE unique_code = ? AND status = 'pending' 
            LIMIT 1
        ");
        $stmt->bind_param("s", $unique_code);
        $stmt->execute();
        $result = $stmt->get_result();
        $transaction = $result->fetch_assoc();
        
        if (!$transaction) {
            $conn->rollback();
            webhook_log("Transaction not found or already processed: {$unique_code}", 'WARNING');
            return ['success' => false, 'message' => 'Không tìm thấy giao dịch chờ xử lý'];
        }
        
        $transaction_id = $transaction['transaction_id'];
        $user_id = $transaction['user_id'];
        $expected_amount = (float)$transaction['amount_paid'];
        
        // Kiểm tra số tiền
        if (abs($amount - $expected_amount) > 1000) {
            $conn->rollback();
            webhook_log("Amount mismatch: expected={$expected_amount}, received={$amount}", 'ERROR');
            return [
                'success' => false, 
                'message' => 'Số tiền không khớp',
                'expected' => $expected_amount,
                'received' => $amount
            ];
        }
        
        // Update transaction
        $update_desc = "Thanh toán qua NH - Mã GD: {$bank_transaction_id}";
        $stmt = $conn->prepare("
            UPDATE transactions 
            SET status = 'success', 
                bank_transaction_id = ?,
                description = CONCAT(COALESCE(description, ''), ' | ', ?),
                transaction_date = NOW()
            WHERE transaction_id = ?
        ");
        $stmt->bind_param("ssi", $bank_transaction_id, $update_desc, $transaction_id);
        $stmt->execute();
        
        if ($stmt->affected_rows === 0) {
            throw new Exception("Không thể cập nhật giao dịch");
        }
        
        // Cộng tiền vào balance
        $stmt = $conn->prepare("UPDATE users SET balance = balance + ? WHERE id = ?");
        $stmt->bind_param("di", $amount, $user_id);
        $stmt->execute();
        
        if ($stmt->affected_rows === 0) {
            throw new Exception("Không thể cập nhật số dư");
        }
        
        $conn->commit();
        
        webhook_log("Payment processed: user={$user_id}, amount={$amount}, code={$unique_code}", 'SUCCESS');
        
        return [
            'success' => true, 
            'message' => 'Thanh toán thành công',
            'transaction_id' => $transaction_id,
            'user_id' => $user_id,
            'amount' => $amount,
            'unique_code' => $unique_code
        ];
        
    } catch (Exception $e) {
        $conn->rollback();
        webhook_log("Error: " . $e->getMessage(), 'ERROR');
        return ['success' => false, 'message' => 'Lỗi xử lý: ' . $e->getMessage()];
    }
}

// ============ MAIN ============

$initial_payload = [];

try {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        json_response(['success' => false, 'message' => 'Method not allowed'], 405);
    }
    
    if (!check_ip_whitelist()) {
        json_response(['success' => false, 'message' => 'Forbidden'], 403);
    }
    
    $raw_input = file_get_contents('php://input');
    $payload = json_decode($raw_input, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        webhook_log("Invalid JSON: " . json_last_error_msg(), 'ERROR');
        json_response(['success' => false, 'message' => 'Invalid JSON'], 400);
    }
    
    $initial_payload = $payload;
    
    if (WEBHOOK_DEBUG) {
        webhook_log("Received: " . json_encode($payload, JSON_UNESCAPED_UNICODE), 'DEBUG');
    }
    
    // Parse data
    $data = [];
    if (isset($payload['data'])) {
        $data = $payload['data'];
    } elseif (isset($payload['transactions']) && is_array($payload['transactions'])) {
        $data = $payload['transactions'][0] ?? [];
    } else {
        $data = $payload;
    }
    
    $result = process_payment($conn, $data);
    
    $status_code = $result['success'] ? 200 : 400;
    json_response($result, $status_code);
    
} catch (Exception $e) {
    webhook_log("Fatal: " . $e->getMessage(), 'FATAL');
    json_response(['success' => false, 'message' => 'Internal server error'], 500);
}
