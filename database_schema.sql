-- ============================================
-- Schema cho hệ thống thanh toán tự động
-- ============================================

-- Bảng users (giả sử đã có)
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `balance` decimal(15,2) DEFAULT 0.00,
  `avatar` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_balance` (`balance`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng transactions (giao dịch)
CREATE TABLE IF NOT EXISTS `transactions` (
  `transaction_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `amount_paid` decimal(15,2) NOT NULL COMMENT 'Số tiền (+ nạp, - mua gói)',
  `description` text DEFAULT NULL COMMENT 'Mô tả giao dịch',
  `transaction_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(20) NOT NULL DEFAULT 'pending' COMMENT 'pending, success, failed, cancelled',
  `unique_code` varchar(50) DEFAULT NULL COMMENT 'Mã giao dịch (TS12345)',
  `bank_transaction_id` varchar(100) DEFAULT NULL COMMENT 'Mã GD ngân hàng',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_id`),
  UNIQUE KEY `unique_code` (`unique_code`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_transaction_date` (`transaction_date`),
  KEY `idx_unique_code_status` (`unique_code`, `status`),
  CONSTRAINT `fk_transactions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng service_packages (gói dịch vụ)
CREATE TABLE IF NOT EXISTS `service_packages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package_name` varchar(100) NOT NULL,
  `price` decimal(15,2) NOT NULL,
  `duration_months` int(11) DEFAULT 1,
  `bandwidth` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `status` varchar(20) DEFAULT 'active' COMMENT 'active, inactive',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng user_services (gói đã mua)
CREATE TABLE IF NOT EXISTS `user_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `package_id` int(11) NOT NULL,
  `server` varchar(100) DEFAULT NULL,
  `payment_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expiry_date` timestamp NULL DEFAULT NULL,
  `status` varchar(20) DEFAULT 'active' COMMENT 'active, expired, cancelled',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_package_id` (`package_id`),
  KEY `idx_status` (`status`),
  KEY `idx_expiry_date` (`expiry_date`),
  CONSTRAINT `fk_user_services_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_services_package` FOREIGN KEY (`package_id`) REFERENCES `service_packages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng receiving_accounts (tài khoản ngân hàng nhận tiền)
CREATE TABLE IF NOT EXISTS `receiving_accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bank_name` varchar(100) NOT NULL,
  `account_number` varchar(50) NOT NULL,
  `account_holder` varchar(100) NOT NULL,
  `branch` varchar(100) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'active' COMMENT 'active, inactive',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng webhook_logs (log webhook để debug)
CREATE TABLE IF NOT EXISTS `webhook_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `payload` text DEFAULT NULL COMMENT 'JSON payload nhận được',
  `response` text DEFAULT NULL COMMENT 'Response trả về',
  `status_code` int(11) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `processed` tinyint(1) DEFAULT 0 COMMENT '0=chưa xử lý, 1=đã xử lý',
  `error_message` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_processed` (`processed`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert dữ liệu mẫu
INSERT INTO `receiving_accounts` (`bank_name`, `account_number`, `account_holder`, `branch`, `status`) VALUES
('VPBank', '1234567890', 'NGUYEN VAN A', 'Ho Chi Minh', 'active');

INSERT INTO `service_packages` (`package_name`, `price`, `duration_months`, `bandwidth`, `description`, `status`) VALUES
('Gói Basic', 50000.00, 1, '50GB', 'Gói cơ bản cho người dùng cá nhân', 'active'),
('Gói Premium', 100000.00, 1, '200GB', 'Gói cao cấp với băng thông lớn', 'active'),
('Gói Enterprise', 200000.00, 1, 'Unlimited', 'Gói doanh nghiệp không giới hạn', 'active');

-- Tạo user demo (password: demo123, hash bằng bcrypt)
-- INSERT INTO `users` (`username`, `email`, `full_name`, `password`, `balance`) VALUES
-- ('demo', 'demo@example.com', 'Demo User', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 0.00);
