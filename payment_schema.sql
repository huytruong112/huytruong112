-- =====================================================
-- CẬP NHẬT DATABASE CHO HỆ THỐNG THANH TOÁN TỰ ĐỘNG
-- =====================================================
-- Chạy file SQL này để tạo bảng payment_logs và cập nhật bảng transactions

-- 1. Tạo bảng payment_logs để lưu log thanh toán tự động
CREATE TABLE IF NOT EXISTS `payment_logs` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `transaction_id` INT(11) DEFAULT NULL COMMENT 'ID giao dịch từ bảng transactions',
  `user_id` INT(11) DEFAULT NULL COMMENT 'ID user',
  `amount` DECIMAL(15,2) NOT NULL COMMENT 'Số tiền thực tế nhận được',
  `expected_amount` DECIMAL(15,2) DEFAULT NULL COMMENT 'Số tiền mong đợi',
  `unique_code` VARCHAR(50) DEFAULT NULL COMMENT 'Mã giao dịch (TSxxxxx)',
  `description` TEXT COMMENT 'Nội dung chuyển khoản',
  `reference_number` VARCHAR(100) DEFAULT NULL COMMENT 'Mã tham chiếu từ ngân hàng',
  `source` VARCHAR(50) DEFAULT NULL COMMENT 'Nguồn: casso, payos, bank, generic',
  `status` VARCHAR(20) DEFAULT 'success' COMMENT 'success, failed, duplicate',
  `raw_data` TEXT COMMENT 'Dữ liệu JSON gốc từ webhook',
  `ip_address` VARCHAR(50) DEFAULT NULL COMMENT 'IP gọi webhook',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời gian xử lý',
  PRIMARY KEY (`id`),
  KEY `idx_transaction_id` (`transaction_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_unique_code` (`unique_code`),
  KEY `idx_reference_number` (`reference_number`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Log thanh toán tự động';

-- 2. Thêm cột updated_at vào bảng transactions (nếu chưa có)
ALTER TABLE `transactions` 
ADD COLUMN `updated_at` DATETIME DEFAULT NULL COMMENT 'Thời gian cập nhật' AFTER `transaction_date`;

-- 3. Thêm index cho bảng transactions để tìm kiếm nhanh hơn
ALTER TABLE `transactions` 
ADD INDEX `idx_unique_code` (`unique_code`),
ADD INDEX `idx_status` (`status`),
ADD INDEX `idx_user_status` (`user_id`, `status`);

-- 4. Tạo bảng notifications (nếu chưa có) để gửi thông báo cho user
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL COMMENT 'ID user nhận thông báo',
  `title` VARCHAR(255) NOT NULL COMMENT 'Tiêu đề thông báo',
  `message` TEXT NOT NULL COMMENT 'Nội dung thông báo',
  `type` VARCHAR(50) DEFAULT 'info' COMMENT 'info, success, warning, error',
  `is_read` TINYINT(1) DEFAULT 0 COMMENT '0=chưa đọc, 1=đã đọc',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_is_read` (`is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Thông báo cho user';

-- 5. Tạo stored procedure để tự động hủy giao dịch quá hạn
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS `cancel_expired_transactions`()
BEGIN
    -- Hủy các giao dịch pending quá 24h
    UPDATE transactions 
    SET status = 'cancelled', 
        updated_at = NOW()
    WHERE status = 'pending' 
    AND TIMESTAMPDIFF(SECOND, transaction_date, NOW()) > 86400;
    
    SELECT ROW_COUNT() as cancelled_count;
END$$

DELIMITER ;

-- 6. Tạo event để tự động chạy procedure hủy giao dịch (chạy mỗi giờ)
-- Lưu ý: Cần bật event_scheduler trong MySQL
-- SET GLOBAL event_scheduler = ON;

CREATE EVENT IF NOT EXISTS `auto_cancel_expired_transactions`
ON SCHEDULE EVERY 1 HOUR
STARTS CURRENT_TIMESTAMP
DO CALL cancel_expired_transactions();

-- 7. Tạo view để xem thống kê thanh toán
CREATE OR REPLACE VIEW `payment_statistics` AS
SELECT 
    DATE(created_at) as payment_date,
    source,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM payment_logs
GROUP BY DATE(created_at), source
ORDER BY payment_date DESC, source;

-- 8. Insert một số dữ liệu mẫu để test (TÙY CHỌN - xóa nếu không cần)
-- INSERT INTO transactions (user_id, amount_paid, transaction_date, status, unique_code) 
-- VALUES (1, 100000, NOW(), 'pending', 'TS12345');

-- =====================================================
-- HOÀN TẤT CẬP NHẬT DATABASE
-- =====================================================
-- Sau khi chạy file SQL này:
-- 1. Kiểm tra bảng payment_logs đã được tạo
-- 2. Kiểm tra event_scheduler: SHOW VARIABLES LIKE 'event_scheduler';
-- 3. Xem các event: SHOW EVENTS;
-- 4. Test thử webhook: https://yourdomain.com/payment_webhook.php?test=1
