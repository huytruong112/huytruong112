<?php
/**
 * API Webhook - Tự động xác nhận thanh toán
 * 
 * API này nhận thông báo từ ngân hàng (qua service trung gian như Casso, VietQR, etc.)
 * và tự động xác nhận giao dịch khi chuyển khoản thành công.
 * 
 * Flow:
 * 1. Nhận POST request từ webhook
 * 2. Xác thực request (signature/token)
 * 3. Parse dữ liệu (số tiền, nội dung CK)
 * 4. Tìm transaction theo unique_code trong nội dung
 * 5. Cập nhật status='success' và cộng tiền vào balance
 * 6. Trả về response
 */

// Thiết lập múi giờ
date_default_timezone_set('Asia/Ho_Chi_Minh');

// Load config
require_once __DIR__ . '/config_payment.php';
require_once __DIR__ . '/db.php';

// Headers cho API
header('Content-Type: application/json; charset=utf-8');

/**
 * Ghi log
 */
function webhook_log(string $message, string $level = 'INFO'): void {
    $logFile = WEBHOOK_LOG_FILE;
    $logDir = dirname($logFile);
    
    if (!is_dir($logDir)) {
        @mkdir($logDir, 0755, true);
    }
    
    $timestamp = date('Y-m-d H:i:s');
    $logMessage = "[{$timestamp}] [{$level}] {$message}\n";
    @file_put_contents($logFile, $logMessage, FILE_APPEND | LOCK_EX);
}

/**
 * Trả về JSON response và exit
 */
function json_response(array $data, int $status = 200): void {
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit();
}

/**
 * Kiểm tra IP whitelist
 */
function check_ip_whitelist(): bool {
    if (!CHECK_IP_WHITELIST) {
        return true;
    }
    
    $client_ip = $_SERVER['REMOTE_ADDR'] ?? '';
    if (in_array($client_ip, ALLOWED_IPS, true)) {
        return true;
    }
    
    webhook_log("Blocked IP: {$client_ip}", 'WARNING');
    return false;
}

/**
 * Xác thực webhook signature
 * Tuỳ thuộc vào service bạn dùng (Casso, VietQR, etc.), có thể cần điều chỉnh
 */
function verify_webhook_signature(array $payload): bool {
    // Lấy signature từ header hoặc payload
    $signature = $_SERVER['HTTP_X_WEBHOOK_SIGNATURE'] ?? $payload['signature'] ?? '';
    
    if (empty($signature)) {
        webhook_log("Missing signature", 'WARNING');
        return false; // Bỏ qua check signature nếu không có (cho test)
    }
    
    // Tính signature dựa trên payload
    $calculated = hash_hmac('sha256', json_encode($payload), WEBHOOK_SECRET_KEY);
    
    if (!hash_equals($calculated, $signature)) {
        webhook_log("Invalid signature", 'ERROR');
        return false;
    }
    
    return true;
}

/**
 * Tìm unique_code trong nội dung chuyển khoản
 * Hỗ trợ nhiều format: TS12345, ts12345, TS 12345, etc.
 */
function extract_unique_code(string $content): ?string {
    // Chuẩn hóa: bỏ dấu, space, chuyển về uppercase
    $normalized = strtoupper(trim($content));
    
    // Pattern: TS + 5 chữ số (có thể có space/dash)
    if (preg_match('/TS[\s\-]?(\d{5})/', $normalized, $matches)) {
        return 'TS' . $matches[1];
    }
    
    return null;
}

/**
 * Xử lý giao dịch thanh toán
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
    
    // Tìm unique_code
    $unique_code = extract_unique_code($content);
    if (!$unique_code) {
        webhook_log("Cannot extract unique_code from: {$content}", 'WARNING');
        return ['success' => false, 'message' => 'Không tìm thấy mã giao dịch trong nội dung'];
    }
    
    // Bắt đầu transaction
    $conn->begin_transaction();
    
    try {
        // Tìm giao dịch pending
        $stmt = $conn->prepare(
            "SELECT transaction_id, user_id, amount_paid, status 
             FROM transactions 
             WHERE unique_code = ? 
             AND status = 'pending' 
             LIMIT 1"
        );
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
        
        // Kiểm tra số tiền khớp (cho phép sai số nhỏ)
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
        
        // Cập nhật transaction thành success
        $update_desc = "Thanh toán qua ngân hàng - Mã GD NH: {$bank_transaction_id}";
        $stmt = $conn->prepare(
            "UPDATE transactions 
             SET status = 'success', 
                 description = CONCAT(COALESCE(description, ''), ' | ', ?),
                 transaction_date = NOW()
             WHERE transaction_id = ?"
        );
        $stmt->bind_param("si", $update_desc, $transaction_id);
        $stmt->execute();
        
        if ($stmt->affected_rows === 0) {
            throw new Exception("Không thể cập nhật giao dịch");
        }
        
        // Cộng tiền vào balance
        $stmt = $conn->prepare(
            "UPDATE users 
             SET balance = balance + ? 
             WHERE id = ?"
        );
        $stmt->bind_param("di", $amount, $user_id);
        $stmt->execute();
        
        if ($stmt->affected_rows === 0) {
            throw new Exception("Không thể cập nhật số dư");
        }
        
        // Commit
        $conn->commit();
        
        webhook_log(
            "Payment processed successfully: user_id={$user_id}, amount={$amount}, code={$unique_code}", 
            'SUCCESS'
        );
        
        return [
            'success' => true, 
            'message' => 'Thanh toán thành công',
            'transaction_id' => $transaction_id,
            'user_id' => $user_id,
            'amount' => $amount
        ];
        
    } catch (Exception $e) {
        $conn->rollback();
        webhook_log("Error processing payment: " . $e->getMessage(), 'ERROR');
        return ['success' => false, 'message' => 'Lỗi xử lý: ' . $e->getMessage()];
    }
}

// ============ MAIN LOGIC ============

try {
    // Chỉ chấp nhận POST
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        json_response(['success' => false, 'message' => 'Method not allowed'], 405);
    }
    
    // Kiểm tra IP whitelist
    if (!check_ip_whitelist()) {
        json_response(['success' => false, 'message' => 'Forbidden'], 403);
    }
    
    // Đọc payload
    $raw_input = file_get_contents('php://input');
    $payload = json_decode($raw_input, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        webhook_log("Invalid JSON: " . json_last_error_msg(), 'ERROR');
        json_response(['success' => false, 'message' => 'Invalid JSON'], 400);
    }
    
    if (WEBHOOK_DEBUG) {
        webhook_log("Received payload: " . json_encode($payload, JSON_UNESCAPED_UNICODE), 'DEBUG');
    }
    
    // Xác thực signature (nếu cần)
    // if (!verify_webhook_signature($payload)) {
    //     json_response(['success' => false, 'message' => 'Invalid signature'], 401);
    // }
    
    // Parse data theo format của service bạn dùng
    // Ví dụ format Casso:
    // {
    //   "id": 123456,
    //   "tid": "FT21123456789",
    //   "description": "TS12345 Nap tien",
    //   "amount": 100000,
    //   "when": "2024-01-01 10:00:00"
    // }
    
    // Hoặc format VietQR/custom:
    // {
    //   "transaction_id": "ABC123",
    //   "amount": 100000,
    //   "content": "TS12345",
    //   "date": "2024-01-01 10:00:00"
    // }
    
    // Chuẩn hóa data
    $data = [];
    
    // Hỗ trợ nhiều format
    if (isset($payload['data'])) {
        // Format nested
        $data = $payload['data'];
    } elseif (isset($payload['transactions']) && is_array($payload['transactions'])) {
        // Format array transactions
        $data = $payload['transactions'][0] ?? [];
    } else {
        // Format flat
        $data = $payload;
    }
    
    // Xử lý thanh toán
    $result = process_payment($conn, $data);
    
    // Trả về response
    $status_code = $result['success'] ? 200 : 400;
    json_response($result, $status_code);
    
} catch (Exception $e) {
    webhook_log("Fatal error: " . $e->getMessage(), 'FATAL');
    json_response(['success' => false, 'message' => 'Internal server error'], 500);
}
