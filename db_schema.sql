-- =====================================================
-- Database Schema cho Hệ Thống Thanh Toán Tự Động
-- =====================================================

-- Cập nhật bảng transactions
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NULL DEFAULT NULL 
AFTER status;

-- Thêm index để tối ưu performance
ALTER TABLE transactions 
ADD INDEX idx_status (status);

ALTER TABLE transactions 
ADD INDEX idx_unique_code (unique_code);

ALTER TABLE transactions 
ADD INDEX idx_user_status (user_id, status);

ALTER TABLE transactions 
ADD INDEX idx_transaction_date (transaction_date);

-- Thêm comment cho các cột
ALTER TABLE transactions 
MODIFY COLUMN status ENUM('pending', 'success', 'cancelled', 'failed') DEFAULT 'pending' 
COMMENT 'Trạng thái: pending=chờ xử lý, success=thành công, cancelled=đã hủy, failed=thất bại';

ALTER TABLE transactions 
MODIFY COLUMN unique_code VARCHAR(50) NOT NULL 
COMMENT 'Mã giao dịch unique dùng làm nội dung chuyển khoản (VD: TS12345)';

-- Tạo bảng payment_logs để tracking (optional)
CREATE TABLE IF NOT EXISTS payment_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NULL,
    unique_code VARCHAR(50) NULL,
    action VARCHAR(50) NOT NULL COMMENT 'created, checked, success, failed, cancelled',
    message TEXT NULL,
    details JSON NULL COMMENT 'Chi tiết dạng JSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_unique_code (unique_code),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Log các hoạt động liên quan đến thanh toán';

-- Tạo bảng bank_transactions để lưu cache giao dịch từ ngân hàng (optional)
CREATE TABLE IF NOT EXISTS bank_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bank_transaction_id VARCHAR(100) NOT NULL COMMENT 'ID giao dịch từ ngân hàng',
    amount DECIMAL(15,2) NOT NULL,
    description TEXT NULL COMMENT 'Nội dung giao dịch',
    transaction_date DATETIME NOT NULL,
    transaction_type ENUM('IN', 'OUT') DEFAULT 'IN',
    balance_after DECIMAL(15,2) NULL,
    matched TINYINT(1) DEFAULT 0 COMMENT '1=đã match với transaction, 0=chưa match',
    matched_transaction_id INT NULL,
    raw_data JSON NULL COMMENT 'Dữ liệu thô từ API ngân hàng',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_bank_tx (bank_transaction_id),
    INDEX idx_matched (matched),
    INDEX idx_transaction_date (transaction_date),
    FOREIGN KEY (matched_transaction_id) REFERENCES transactions(transaction_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Cache giao dịch từ ngân hàng để tránh query lại nhiều lần';

-- Tạo bảng webhook_logs để tracking webhook (optional)
CREATE TABLE IF NOT EXISTS webhook_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    webhook_type VARCHAR(50) NOT NULL,
    payload TEXT NOT NULL,
    signature VARCHAR(255) NULL,
    ip_address VARCHAR(45) NULL,
    processed TINYINT(1) DEFAULT 0,
    response TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_processed (processed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Log tất cả webhook requests';

-- View để xem thống kê thanh toán
CREATE OR REPLACE VIEW v_payment_statistics AS
SELECT 
    DATE(transaction_date) as date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count,
    SUM(CASE WHEN status = 'success' THEN amount_paid ELSE 0 END) as total_amount_success,
    AVG(CASE WHEN status = 'success' AND updated_at IS NOT NULL 
        THEN TIMESTAMPDIFF(SECOND, transaction_date, updated_at) 
        ELSE NULL END) as avg_processing_time_seconds
FROM transactions
WHERE transaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(transaction_date)
ORDER BY date DESC;

-- Stored Procedure để xử lý thanh toán thành công (optional - có thể dùng trong PHP)
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS sp_process_payment_success(
    IN p_transaction_id INT,
    IN p_user_id INT,
    IN p_amount DECIMAL(15,2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error occurred' as status;
    END;

    START TRANSACTION;
    
    -- Update transaction status
    UPDATE transactions 
    SET status = 'success', 
        updated_at = NOW() 
    WHERE transaction_id = p_transaction_id 
    AND status = 'pending';
    
    -- Update user balance
    UPDATE users 
    SET balance = balance + p_amount 
    WHERE id = p_user_id;
    
    -- Log the action
    INSERT INTO payment_logs (transaction_id, action, message, created_at)
    VALUES (p_transaction_id, 'success', CONCAT('Payment processed: ', p_amount), NOW());
    
    COMMIT;
    SELECT 'Success' as status;
END //

DELIMITER ;

-- Trigger để tự động log khi transaction status thay đổi
DELIMITER //

CREATE TRIGGER IF NOT EXISTS after_transaction_update
AFTER UPDATE ON transactions
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO payment_logs (
            transaction_id, 
            unique_code, 
            action, 
            message, 
            details
        )
        VALUES (
            NEW.transaction_id,
            NEW.unique_code,
            CONCAT('status_change_', NEW.status),
            CONCAT('Status changed from ', OLD.status, ' to ', NEW.status),
            JSON_OBJECT(
                'old_status', OLD.status,
                'new_status', NEW.status,
                'amount', NEW.amount_paid,
                'user_id', NEW.user_id
            )
        );
    END IF;
END //

DELIMITER ;

-- =====================================================
-- Queries hữu ích
-- =====================================================

-- Xem giao dịch pending
-- SELECT * FROM transactions WHERE status = 'pending' ORDER BY transaction_date DESC;

-- Xem giao dịch thành công trong 24h
-- SELECT * FROM transactions WHERE status = 'success' AND transaction_date >= DATE_SUB(NOW(), INTERVAL 24 HOUR);

-- Xem thống kê
-- SELECT * FROM v_payment_statistics;

-- Xem log
-- SELECT * FROM payment_logs ORDER BY created_at DESC LIMIT 100;

-- Tìm giao dịch quá hạn (pending > 24h)
-- SELECT * FROM transactions WHERE status = 'pending' AND transaction_date < DATE_SUB(NOW(), INTERVAL 24 HOUR);

-- Xem user có giao dịch thành công nhiều nhất
-- SELECT u.username, COUNT(*) as total_success, SUM(t.amount_paid) as total_amount
-- FROM transactions t
-- JOIN users u ON t.user_id = u.id
-- WHERE t.status = 'success'
-- GROUP BY u.id
-- ORDER BY total_success DESC
-- LIMIT 10;
