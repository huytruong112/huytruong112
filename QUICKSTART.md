# ⚡ Quick Start - 5 Phút Chạy Được!

## 🎯 Mục Tiêu

Trong 5 phút, bạn sẽ có hệ thống webhook thanh toán chạy local.

---

## 📋 Checklist

- [ ] PHP 7.4+ installed
- [ ] MySQL/MariaDB running
- [ ] Composer (optional)
- [ ] Terminal/Command line

---

## 🚀 Bước 1: Setup Database (1 phút)

### Tạo database:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE payment_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'payment_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON payment_system.* TO 'payment_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Import schema:

```bash
mysql -u payment_user -p payment_system < database_schema.sql
```

---

## 🚀 Bước 2: Cấu Hình (1 phút)

### Copy files:

```bash
cp example_db.php db.php
cp example_config_payment.php config_payment.php
```

### Chỉnh sửa `db.php`:

```php
<?php
define('DB_HOST', 'localhost');
define('DB_USER', 'payment_user');
define('DB_PASS', 'your_password');
define('DB_NAME', 'payment_system');

$conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
$conn->set_charset('utf8mb4');
```

### Chỉnh sửa `config_payment.php`:

```php
<?php
// Để mặc định cho test local
define('WEBHOOK_SECRET_KEY', 'test-secret-key');
define('CHECK_IP_WHITELIST', false); // Tắt check IP khi test
define('WEBHOOK_DEBUG', true);
```

---

## 🚀 Bước 3: Tạo User Test (30 giây)

```bash
mysql -u payment_user -p payment_system
```

```sql
INSERT INTO users (username, email, password, balance)
VALUES ('demo', 'demo@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 0);
-- Password: password
```

---

## 🚀 Bước 4: Test (2 phút)

### Tạo giao dịch test:

```bash
php create_test_transaction.php
```

Output mong đợi:
```
=================================
  TẠO GIAO DỊCH TEST
=================================

User ID: 1 (demo)

Tạo 5 giao dịch test...

✅ TS12345: Tạo thành công (Số tiền: 100,000 VND)
✅ TS67890: Tạo thành công (Số tiền: 50,000 VND)
✅ TS11111: Tạo thành công (Số tiền: 200,000 VND)
✅ TS22222: Tạo thành công (Số tiền: 150,000 VND)
✅ TS99999: Tạo thành công (Số tiền: 75,000 VND)

=================================
Đã tạo: 5 giao dịch
=================================
```

### Test webhook:

```bash
php test_webhook.php
```

Output mong đợi:
```
=================================
  TEST WEBHOOK THANH TOÁN
=================================

URL: http://localhost/api_payment_webhook.php
Số test: 6

--- Test 1: Giao dịch hợp lệ ---
HTTP Code: 200
Response: {"success":true,"message":"Thanh toán thành công",...}
✅ PASSED

--- Test 2: Mã viết thường ---
HTTP Code: 200
Response: {"success":true,...}
✅ PASSED

...

=================================
KẾT QUẢ:
✅ Passed: 4
❌ Failed: 2
=================================
```

---

## 🚀 Bước 5: Xem Logs (30 giây)

```bash
# Tạo thư mục logs nếu chưa có
mkdir -p logs
chmod 755 logs

# Xem log
tail -f logs/payment_webhook.log
```

Output:
```
[2024-01-01 10:00:00] [INFO] Payment processed successfully: user_id=1, amount=100000, code=TS12345
[2024-01-01 10:00:05] [SUCCESS] Payment processed: user=1, amount=50000, code=TS67890
```

---

## 🎉 Hoàn Thành!

Bây giờ bạn đã có:

✅ Database setup xong  
✅ Webhook API chạy local  
✅ Test cases pass  
✅ Logs hoạt động  

---

## 🔥 Test Nhanh Với Curl

```bash
# Test 1: Giao dịch thành công
curl -X POST http://localhost/api_payment_webhook.php \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST001",
    "amount": 100000,
    "description": "TS12345 Test thanh toan"
  }'

# Response:
# {"success":true,"message":"Thanh toán thành công",...}

# Test 2: Kiểm tra balance
mysql -u payment_user -p payment_system -e "SELECT id, username, balance FROM users WHERE id=1;"

# Output:
# +----+----------+----------+
# | id | username | balance  |
# +----+----------+----------+
# |  1 | demo     | 100000.00|
# +----+----------+----------+
```

---

## 📱 Chạy Local Web Server

### Option 1: PHP Built-in Server

```bash
php -S localhost:8000
```

Truy cập: http://localhost:8000/deposit.php

### Option 2: XAMPP/WAMP

1. Copy toàn bộ file vào `htdocs/`
2. Start Apache & MySQL
3. Truy cập: http://localhost/deposit.php

### Option 3: Docker (nếu bạn dùng Docker)

```bash
docker run -d -p 8080:80 -v $(pwd):/var/www/html php:8.1-apache
```

Truy cập: http://localhost:8080/deposit.php

---

## 🐛 Troubleshooting Nhanh

### Lỗi: "Cannot connect to database"

```bash
# Check MySQL running
sudo systemctl status mysql

# Restart MySQL
sudo systemctl restart mysql

# Test connection
mysql -u payment_user -p payment_system
```

### Lỗi: "Permission denied" (logs)

```bash
mkdir -p logs
chmod 755 logs
chown -R www-data:www-data logs/
```

### Lỗi: "Class 'mysqli' not found"

```bash
# Ubuntu/Debian
sudo apt install php-mysqli

# CentOS/RHEL
sudo yum install php-mysqli

# Restart Apache/PHP-FPM
sudo systemctl restart apache2
```

### Webhook không hoạt động

```bash
# 1. Check URL
curl http://localhost/api_payment_webhook.php

# 2. Check logs
tail -f logs/payment_webhook.log

# 3. Check PHP errors
tail -f /var/log/apache2/error.log
```

---

## ➡️ Bước Tiếp Theo

Sau khi test local thành công:

1. 📖 Đọc [SETUP_GUIDE.md](SETUP_GUIDE.md) để deploy lên production
2. 🔌 Xem [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) để tích hợp Casso/VietQR
3. ❓ Có thắc mắc? Xem [FAQ.md](FAQ.md)

---

## 📞 Cần Hỗ Trợ?

- 📧 Email: support.vpn@vpnvietnam.com
- 📱 Hotline: 0826.003.926
- 💬 Zalo: 0826.003.926

---

**Happy Coding! 🚀**
