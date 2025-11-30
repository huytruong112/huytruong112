<?php
/**
 * Script cập nhật cấu trúc database cho tính năng thanh toán tự động
 * Chạy file này MỘT LẦN để cập nhật database
 * 
 * Cách chạy: php update_database_schema.php
 * Hoặc truy cập: https://yourdomain.com/update_database_schema.php
 */

date_default_timezone_set('Asia/Ho_Chi_Minh');

require_once 'db.php';

echo "<h1>Cập nhật Database Schema cho Thanh Toán Tự Động</h1>";
echo "<pre>";

$updates = [];
$errors = [];

try {
    // 1. Thêm cột bank_transaction_ref vào bảng transactions (nếu chưa có)
    echo "1. Kiểm tra và thêm cột bank_transaction_ref...\n";
    
    $check = $conn->query("SHOW COLUMNS FROM transactions LIKE 'bank_transaction_ref'");
    if ($check->num_rows == 0) {
        $sql = "ALTER TABLE transactions ADD COLUMN bank_transaction_ref VARCHAR(100) DEFAULT NULL AFTER unique_code";
        if ($conn->query($sql)) {
            $updates[] = "✓ Đã thêm cột bank_transaction_ref vào bảng transactions";
            echo "✓ Đã thêm cột bank_transaction_ref\n";
        } else {
            $errors[] = "✗ Lỗi khi thêm cột bank_transaction_ref: " . $conn->error;
            echo "✗ Lỗi: " . $conn->error . "\n";
        }
    } else {
        $updates[] = "○ Cột bank_transaction_ref đã tồn tại";
        echo "○ Cột bank_transaction_ref đã tồn tại\n";
    }
    
    // 2. Thêm cột updated_at vào bảng transactions (nếu chưa có)
    echo "\n2. Kiểm tra và thêm cột updated_at...\n";
    
    $check = $conn->query("SHOW COLUMNS FROM transactions LIKE 'updated_at'");
    if ($check->num_rows == 0) {
        $sql = "ALTER TABLE transactions ADD COLUMN updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP AFTER transaction_date";
        if ($conn->query($sql)) {
            $updates[] = "✓ Đã thêm cột updated_at vào bảng transactions";
            echo "✓ Đã thêm cột updated_at\n";
        } else {
            $errors[] = "✗ Lỗi khi thêm cột updated_at: " . $conn->error;
            echo "✗ Lỗi: " . $conn->error . "\n";
        }
    } else {
        $updates[] = "○ Cột updated_at đã tồn tại";
        echo "○ Cột updated_at đã tồn tại\n";
    }
    
    // 3. Thêm index cho cột unique_code để tăng tốc độ tìm kiếm
    echo "\n3. Kiểm tra và thêm index cho unique_code...\n";
    
    $check = $conn->query("SHOW INDEX FROM transactions WHERE Key_name = 'idx_unique_code'");
    if ($check->num_rows == 0) {
        $sql = "ALTER TABLE transactions ADD INDEX idx_unique_code (unique_code)";
        if ($conn->query($sql)) {
            $updates[] = "✓ Đã thêm index cho cột unique_code";
            echo "✓ Đã thêm index cho unique_code\n";
        } else {
            $errors[] = "✗ Lỗi khi thêm index unique_code: " . $conn->error;
            echo "✗ Lỗi: " . $conn->error . "\n";
        }
    } else {
        $updates[] = "○ Index unique_code đã tồn tại";
        echo "○ Index unique_code đã tồn tại\n";
    }
    
    // 4. Thêm index cho cột status để tăng tốc độ tìm kiếm giao dịch pending
    echo "\n4. Kiểm tra và thêm index cho status...\n";
    
    $check = $conn->query("SHOW INDEX FROM transactions WHERE Key_name = 'idx_status'");
    if ($check->num_rows == 0) {
        $sql = "ALTER TABLE transactions ADD INDEX idx_status (status)";
        if ($conn->query($sql)) {
            $updates[] = "✓ Đã thêm index cho cột status";
            echo "✓ Đã thêm index cho status\n";
        } else {
            $errors[] = "✗ Lỗi khi thêm index status: " . $conn->error;
            echo "✗ Lỗi: " . $conn->error . "\n";
        }
    } else {
        $updates[] = "○ Index status đã tồn tại";
        echo "○ Index status đã tồn tại\n";
    }
    
    // 5. Tạo bảng payment_logs (nếu chưa có)
    echo "\n5. Kiểm tra và tạo bảng payment_logs...\n";
    
    $check = $conn->query("SHOW TABLES LIKE 'payment_logs'");
    if ($check->num_rows == 0) {
        $sql = "CREATE TABLE payment_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id INT,
            user_id INT,
            unique_code VARCHAR(50),
            amount DECIMAL(15,2),
            bank_transaction_ref VARCHAR(100),
            status VARCHAR(50),
            extra_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_transaction (transaction_id),
            INDEX idx_user (user_id),
            INDEX idx_unique_code (unique_code),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
        
        if ($conn->query($sql)) {
            $updates[] = "✓ Đã tạo bảng payment_logs";
            echo "✓ Đã tạo bảng payment_logs\n";
        } else {
            $errors[] = "✗ Lỗi khi tạo bảng payment_logs: " . $conn->error;
            echo "✗ Lỗi: " . $conn->error . "\n";
        }
    } else {
        $updates[] = "○ Bảng payment_logs đã tồn tại";
        echo "○ Bảng payment_logs đã tồn tại\n";
    }
    
    // 6. Kiểm tra và tạo bảng receiving_accounts (nếu chưa có)
    echo "\n6. Kiểm tra và tạo bảng receiving_accounts...\n";
    
    $check = $conn->query("SHOW TABLES LIKE 'receiving_accounts'");
    if ($check->num_rows == 0) {
        $sql = "CREATE TABLE receiving_accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bank_name VARCHAR(100) NOT NULL,
            account_number VARCHAR(50) NOT NULL,
            account_holder VARCHAR(100) NOT NULL,
            branch VARCHAR(100) DEFAULT NULL,
            status ENUM('active', 'inactive') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
        
        if ($conn->query($sql)) {
            $updates[] = "✓ Đã tạo bảng receiving_accounts";
            echo "✓ Đã tạo bảng receiving_accounts\n";
            
            // Thêm tài khoản mẫu
            $insert_sql = "INSERT INTO receiving_accounts (bank_name, account_number, account_holder, branch) 
                          VALUES ('Ngân hàng MB Bank', '0123456789', 'NGUYEN VAN A', 'Chi nhánh Hà Nội')";
            if ($conn->query($insert_sql)) {
                $updates[] = "✓ Đã thêm tài khoản ngân hàng mẫu (vui lòng cập nhật thông tin thực)";
                echo "✓ Đã thêm tài khoản mẫu\n";
            }
        } else {
            $errors[] = "✗ Lỗi khi tạo bảng receiving_accounts: " . $conn->error;
            echo "✗ Lỗi: " . $conn->error . "\n";
        }
    } else {
        $updates[] = "○ Bảng receiving_accounts đã tồn tại";
        echo "○ Bảng receiving_accounts đã tồn tại\n";
    }
    
    // 7. Tạo thư mục logs (nếu chưa có)
    echo "\n7. Kiểm tra và tạo thư mục logs...\n";
    
    $log_dir = __DIR__ . '/logs';
    if (!is_dir($log_dir)) {
        if (mkdir($log_dir, 0755, true)) {
            $updates[] = "✓ Đã tạo thư mục logs";
            echo "✓ Đã tạo thư mục logs\n";
            
            // Tạo file .htaccess để bảo vệ thư mục logs
            file_put_contents($log_dir . '/.htaccess', "Deny from all");
            $updates[] = "✓ Đã tạo file .htaccess bảo vệ thư mục logs";
            echo "✓ Đã tạo file .htaccess\n";
        } else {
            $errors[] = "✗ Lỗi khi tạo thư mục logs";
            echo "✗ Không thể tạo thư mục logs\n";
        }
    } else {
        $updates[] = "○ Thư mục logs đã tồn tại";
        echo "○ Thư mục logs đã tồn tại\n";
    }
    
} catch (Exception $e) {
    $errors[] = "✗ Exception: " . $e->getMessage();
    echo "\n✗ Exception: " . $e->getMessage() . "\n";
}

// Tổng kết
echo "\n" . str_repeat("=", 60) . "\n";
echo "TỔNG KẾT CẬP NHẬT DATABASE\n";
echo str_repeat("=", 60) . "\n\n";

if (!empty($updates)) {
    echo "Các thay đổi đã thực hiện:\n";
    foreach ($updates as $update) {
        echo "  $update\n";
    }
}

if (!empty($errors)) {
    echo "\nCác lỗi gặp phải:\n";
    foreach ($errors as $error) {
        echo "  $error\n";
    }
}

if (empty($errors)) {
    echo "\n✓✓✓ CẬP NHẬT DATABASE THÀNH CÔNG! ✓✓✓\n";
    echo "\nBạn có thể xóa file update_database_schema.php này sau khi cập nhật xong.\n";
} else {
    echo "\n✗✗✗ CÓ LỖI XẢY RA! VUI LÒNG KIỂM TRA LẠI. ✗✗✗\n";
}

echo "\n</pre>";
