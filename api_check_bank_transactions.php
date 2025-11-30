<?php
/**
 * API Kiểm tra giao dịch ngân hàng tự động (Cron Job)
 * File này sẽ được chạy định kỳ bởi cron job để kiểm tra giao dịch ngân hàng
 * 
 * Cài đặt cron job (ví dụ chạy mỗi phút):
 * * * * * * php /path/to/api_check_bank_transactions.php
 * 
 * Hoặc gọi qua HTTP:
 * * * * * * curl https://yourdomain.com/api_check_bank_transactions.php?secret=YOUR_SECRET_KEY
 */

// Thiết lập múi giờ
date_default_timezone_set('Asia/Ho_Chi_Minh');

// Kiểm tra xem script được chạy từ CLI hay HTTP
$is_cli = (php_sapi_name() === 'cli');

if (!$is_cli) {
    // Nếu chạy qua HTTP, cần xác thực secret key
    $secret_key = $_GET['secret'] ?? '';
    require_once 'config_payment.php';
    
    if ($secret_key !== API_SECRET_KEY) {
        http_response_code(403);
        die(json_encode(['success' => false, 'message' => 'Invalid secret key']));
    }
    
    header('Content-Type: application/json; charset=utf-8');
}

require_once 'db.php';
require_once 'payment_helper.php';
require_once 'config_payment.php';

// Khởi tạo Payment Helper
$paymentHelper = new PaymentHelper($conn);

$paymentHelper->logPayment("=== Bắt đầu kiểm tra giao dịch tự động ===");

try {
    // 1. Hủy các giao dịch timeout
    $cancelled_count = $paymentHelper->cancelTimeoutTransactions();
    if ($cancelled_count > 0) {
        $paymentHelper->logPayment("Đã hủy $cancelled_count giao dịch timeout");
    }
    
    // 2. Lấy danh sách giao dịch pending
    $pending_transactions = $paymentHelper->getPendingTransactions();
    
    if (empty($pending_transactions)) {
        $paymentHelper->logPayment("Không có giao dịch pending nào cần kiểm tra");
        echo json_encode([
            'success' => true,
            'message' => 'No pending transactions',
            'checked' => 0
        ]);
        exit;
    }
    
    $paymentHelper->logPayment("Tìm thấy " . count($pending_transactions) . " giao dịch pending");
    
    // 3. Kiểm tra từng giao dịch với ngân hàng
    $processed_count = 0;
    $success_count = 0;
    
    foreach ($pending_transactions as $transaction) {
        $unique_code = $transaction['unique_code'];
        $expected_amount = (float)$transaction['amount_paid'];
        
        $paymentHelper->logPayment("Kiểm tra giao dịch: $unique_code, số tiền: $expected_amount");
        
        // Gọi API ngân hàng để kiểm tra
        $bank_result = checkBankTransaction($unique_code, $expected_amount);
        
        if ($bank_result['found']) {
            // Tìm thấy giao dịch khớp trong ngân hàng
            $paymentHelper->logPayment("Tìm thấy giao dịch khớp: $unique_code");
            
            $result = $paymentHelper->processAutoPayment(
                $unique_code,
                $bank_result['amount'],
                $bank_result['transaction_ref'] ?? '',
                $bank_result['extra_data'] ?? []
            );
            
            if ($result['success']) {
                $success_count++;
                $paymentHelper->logPayment("Xử lý thanh toán thành công: $unique_code");
            }
            
            $processed_count++;
        }
    }
    
    $paymentHelper->logPayment("=== Kết thúc kiểm tra: Đã xử lý $processed_count giao dịch, thành công $success_count ===");
    
    echo json_encode([
        'success' => true,
        'message' => 'Check completed',
        'pending_count' => count($pending_transactions),
        'processed' => $processed_count,
        'success' => $success_count,
        'cancelled' => $cancelled_count
    ]);
    
} catch (Exception $e) {
    $paymentHelper->logPayment("Lỗi khi kiểm tra giao dịch: " . $e->getMessage());
    echo json_encode([
        'success' => false,
        'message' => 'Error: ' . $e->getMessage()
    ]);
}

/**
 * Kiểm tra giao dịch với ngân hàng
 * Hàm này cần được tùy chỉnh theo API của từng ngân hàng
 * 
 * @param string $unique_code Mã giao dịch cần tìm
 * @param float $expected_amount Số tiền mong đợi
 * @return array Kết quả tìm kiếm
 */
function checkBankTransaction($unique_code, $expected_amount) {
    global $bank_api_config, $paymentHelper;
    
    if (!$bank_api_config['enabled']) {
        return ['found' => false];
    }
    
    $bank_type = $bank_api_config['bank_type'];
    
    switch ($bank_type) {
        case 'mbbank':
            return checkMBBankTransaction($unique_code, $expected_amount);
            
        case 'vcb':
            return checkVCBTransaction($unique_code, $expected_amount);
            
        case 'acb':
            return checkACBTransaction($unique_code, $expected_amount);
            
        case 'techcombank':
            return checkTechcombankTransaction($unique_code, $expected_amount);
            
        case 'vietqr':
            return checkVietQRTransaction($unique_code, $expected_amount);
            
        default:
            $paymentHelper->logPayment("Loại ngân hàng không được hỗ trợ: $bank_type");
            return ['found' => false];
    }
}

/**
 * Kiểm tra giao dịch MB Bank
 * Cần API credentials từ MB Bank
 */
function checkMBBankTransaction($unique_code, $expected_amount) {
    global $bank_api_config, $paymentHelper;
    
    try {
        // Ví dụ: Gọi API MB Bank (cần có API credentials)
        $api_url = $bank_api_config['api_url'];
        $account_number = $bank_api_config['account_number'];
        
        // Lấy giao dịch trong 24h gần nhất
        $from_date = date('Y-m-d', strtotime('-1 day'));
        $to_date = date('Y-m-d');
        
        // Gọi API (pseudo code - cần thay đổi theo API thực tế)
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => "$api_url/transactions?account=$account_number&from=$from_date&to=$to_date",
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $bank_api_config['api_token'],
                'Content-Type: application/json'
            ]
        ]);
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            $paymentHelper->logPayment("Lỗi khi gọi API MB Bank: HTTP $http_code");
            return ['found' => false];
        }
        
        $data = json_decode($response, true);
        
        // Tìm giao dịch khớp với unique_code và amount
        foreach ($data['transactions'] ?? [] as $trans) {
            $description = $trans['description'] ?? '';
            $amount = (float)($trans['amount'] ?? 0);
            
            // Kiểm tra nội dung chuyển khoản có chứa unique_code
            if (stripos($description, $unique_code) !== false && abs($amount - $expected_amount) <= 1) {
                return [
                    'found' => true,
                    'amount' => $amount,
                    'transaction_ref' => $trans['transactionId'] ?? '',
                    'extra_data' => [
                        'bank' => 'mbbank',
                        'transaction_date' => $trans['date'] ?? '',
                        'description' => $description
                    ]
                ];
            }
        }
        
        return ['found' => false];
        
    } catch (Exception $e) {
        $paymentHelper->logPayment("Exception khi kiểm tra MB Bank: " . $e->getMessage());
        return ['found' => false];
    }
}

/**
 * Kiểm tra giao dịch VCB (Vietcombank)
 */
function checkVCBTransaction($unique_code, $expected_amount) {
    // Tương tự như MB Bank, cần tùy chỉnh theo API VCB
    return ['found' => false];
}

/**
 * Kiểm tra giao dịch ACB
 */
function checkACBTransaction($unique_code, $expected_amount) {
    // Tương tự như MB Bank, cần tùy chỉnh theo API ACB
    return ['found' => false];
}

/**
 * Kiểm tra giao dịch Techcombank
 */
function checkTechcombankTransaction($unique_code, $expected_amount) {
    // Tương tự như MB Bank, cần tùy chỉnh theo API Techcombank
    return ['found' => false];
}

/**
 * Kiểm tra giao dịch qua VietQR API
 * VietQR là dịch vụ bên thứ 3 có thể kiểm tra giao dịch của nhiều ngân hàng
 */
function checkVietQRTransaction($unique_code, $expected_amount) {
    global $paymentHelper;
    
    try {
        // Gọi VietQR API
        $api_url = VIETQR_API_URL;
        $api_key = VIETQR_API_KEY;
        
        if (empty($api_key)) {
            return ['found' => false];
        }
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $api_url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'x-api-key: ' . $api_key,
                'Content-Type: application/json'
            ]
        ]);
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            $paymentHelper->logPayment("Lỗi khi gọi VietQR API: HTTP $http_code");
            return ['found' => false];
        }
        
        $data = json_decode($response, true);
        
        // Tìm giao dịch khớp
        foreach ($data['transactions'] ?? [] as $trans) {
            $description = $trans['description'] ?? '';
            $amount = (float)($trans['amount'] ?? 0);
            
            if (stripos($description, $unique_code) !== false && abs($amount - $expected_amount) <= 1) {
                return [
                    'found' => true,
                    'amount' => $amount,
                    'transaction_ref' => $trans['id'] ?? '',
                    'extra_data' => [
                        'bank' => 'vietqr',
                        'transaction_date' => $trans['date'] ?? '',
                        'description' => $description
                    ]
                ];
            }
        }
        
        return ['found' => false];
        
    } catch (Exception $e) {
        $paymentHelper->logPayment("Exception khi kiểm tra VietQR: " . $e->getMessage());
        return ['found' => false];
    }
}
