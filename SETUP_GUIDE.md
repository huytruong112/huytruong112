# 📖 HƯỚNG DẪN CÀI ĐÁT CHI TIẾT

## Bước 1: Chuẩn bị

### Yêu cầu hệ thống
- ✅ PHP 7.4 trở lên
- ✅ MySQL 5.7+ / MariaDB 10.3+
- ✅ Apache/Nginx
- ✅ HTTPS (SSL certificate) - Bắt buộc
- ✅ Extension: mysqli, curl, json

### Kiểm tra PHP version
```bash
php -v
```

### Kiểm tra extensions
```bash
php -m | grep -E "mysqli|curl|json"
```

## Bước 2: Upload code lên server

### Cách 1: FTP/SFTP
Upload toàn bộ thư mục `/workspace/` lên server vào thư mục web root (ví dụ: `/var/www/html/`)

### Cách 2: Git
```bash
cd /var/www/html
git clone https://github.com/your-repo/vpn-payment.git .
```

## Bước 3: Phân quyền thư mục

```bash
# Tạo thư mục logs
mkdir -p logs
chmod 755 logs

# Phân quyền các file
chmod 644 *.php
chmod 644 *.md
chmod 644 .htaccess
chmod 600 payment_config.php  # File nhạy cảm
chmod 600 db.php              # File nhạy cảm

# Phân quyền owner (thay www-data bằng user của web server)
chown -R www-data:www-data /var/www/html
```

## Bước 4: Cập nhật Database

### Cách 1: phpMyAdmin
1. Đăng nhập phpMyAdmin
2. Chọn database `vpn_vietnam`
3. Vào tab **Import**
4. Chọn file `payment_schema.sql`
5. Click **Go**

### Cách 2: Command line
```bash
mysql -u root -p vpn_vietnam < payment_schema.sql
```

### Xác nhận
Kiểm tra các bảng đã được tạo:
```sql
SHOW TABLES LIKE '%payment%';
-- Kết quả phải có: payment_logs
```

## Bước 5: Cấu hình Database

Mở file `db.php` và chỉnh sửa:

```php
define('DB_HOST', 'localhost');      // Host MySQL
define('DB_USER', 'your_username');  // Username
define('DB_PASS', 'your_password');  // Password
define('DB_NAME', 'vpn_vietnam');    // Tên database
```

**Lưu ý:** Đảm bảo user MySQL có đủ quyền:
```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON vpn_vietnam.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
```

## Bước 6: Cấu hình API Thanh Toán

Mở file `payment_config.php`:

### 1. Bật thanh toán tự động
```php
define('PAYMENT_ENABLED', true);
define('PAYMENT_DEBUG', true);  // Bật debug khi test, tắt khi production
```

### 2. Đổi Secret Key
```php
// ⚠️ QUAN TRỌNG: Đổi key này!
define('WEBHOOK_SECRET', 'your-random-secret-key-' . bin2hex(random_bytes(16)));
```

### 3. Cấu hình Casso.vn

**Bước 3.1:** Đăng ký tài khoản tại https://casso.vn

**Bước 3.2:** Liên kết tài khoản ngân hàng
- Đăng nhập Casso → **Tài khoản ngân hàng** → **Thêm tài khoản**
- Nhập thông tin đăng nhập Internet Banking
- Hoàn tất kích hoạt

**Bước 3.3:** Lấy API Key
- Vào **Cài đặt** → **Thông tin doanh nghiệp** → **API Key**
- Copy API Key

**Bước 3.4:** Cấu hình trong `payment_config.php`
```php
define('CASSO_ENABLED', true);
define('CASSO_API_KEY', 'AK_CS.xxxxxxxxxxxxx');  // Paste API Key từ Casso
```

**Bước 3.5:** Đăng ký Webhook
- Vào **Cài đặt** → **Webhook**
- Thêm webhook URL:
  ```
  https://yourdomain.com/payment_webhook.php?source=casso
  ```
- Copy **Secure Token** và paste vào config:
  ```php
  define('CASSO_SECURE_TOKEN', 'xxxxxxxxxxxxxx');
  ```
- Chọn event: **Chỉ giao dịch thành công**
- Lưu

### 4. Cấu hình IP Whitelist
```php
define('ALLOWED_IPS', [
    '103.146.23.96',  // IP của Casso.vn
    '103.146.23.97',  
    '103.146.23.98',
    // Thêm IP server của bạn để test
    'YOUR_SERVER_IP',
]);
```

**Lấy IP của server:**
```bash
curl ifconfig.me
```

## Bước 7: Test Hệ Thống

### Test 1: Kiểm tra kết nối database
```bash
php -r "require 'db.php'; echo 'Database OK: ' . \$conn->host_info;"
```

### Test 2: Kiểm tra webhook endpoint
```bash
curl "https://yourdomain.com/payment_webhook.php?test=1"
```

Kết quả mong đợi:
```json
{
  "success": true,
  "message": "Webhook is working"
}
```

### Test 3: Kiểm tra Casso webhook
1. Vào Casso.vn → **Cài đặt** → **Webhook**
2. Click **Test webhook**
3. Xem log tại `logs/payment_webhook.log`

### Test 4: Test giao dịch thực tế

**Bước 4.1:** Tạo giao dịch test trong database
```sql
INSERT INTO transactions (user_id, amount_paid, transaction_date, status, unique_code) 
VALUES (1, 10000, NOW(), 'pending', 'TS99999');
```

**Bước 4.2:** Giả lập webhook
```bash
php test_webhook.php
```

**Bước 4.3:** Kiểm tra kết quả
```sql
-- Kiểm tra transaction đã chuyển thành success
SELECT * FROM transactions WHERE unique_code = 'TS99999';

-- Kiểm tra log
SELECT * FROM payment_logs ORDER BY created_at DESC LIMIT 1;

-- Kiểm tra số dư user
SELECT balance FROM users WHERE id = 1;
```

## Bước 8: Cấu hình Cron Job (Tùy chọn)

### Tự động hủy giao dịch quá hạn

**Mở crontab:**
```bash
crontab -e
```

**Thêm dòng (chạy mỗi giờ):**
```
0 * * * * /usr/bin/php /var/www/html/cron_cancel_expired.php >> /var/www/html/logs/cron.log 2>&1
```

**Kiểm tra cron:**
```bash
crontab -l
```

## Bước 9: Bảo mật

### 1. Bật HTTPS
**Với Let's Encrypt (miễn phí):**
```bash
apt install certbot python3-certbot-apache
certbot --apache -d yourdomain.com
```

### 2. Cấu hình Firewall
```bash
# Chỉ cho phép HTTP, HTTPS, SSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

### 3. Ẩn thông tin PHP
Trong `php.ini`:
```ini
expose_php = Off
display_errors = Off
log_errors = On
error_log = /var/log/php_errors.log
```

### 4. Chặn truy cập file nhạy cảm
File `.htaccess` đã có sẵn rule bảo vệ:
- `payment_config.php`
- `db.php`
- `logs/`

## Bước 10: Monitoring

### Xem log realtime
```bash
tail -f logs/payment_webhook.log
```

### Xem thống kê
```bash
php payment_statistics.php
```

### Kiểm tra database
```sql
-- Xem tổng số giao dịch hôm nay
SELECT COUNT(*) FROM payment_logs WHERE DATE(created_at) = CURDATE();

-- Xem tổng tiền
SELECT SUM(amount) FROM payment_logs WHERE status='success' AND DATE(created_at) = CURDATE();
```

## Bước 11: Production Checklist

Trước khi đưa vào sử dụng thực tế:

- [ ] Đã test webhook thành công
- [ ] Đã test giao dịch thực tế
- [ ] Đã cấu hình HTTPS
- [ ] Đã đổi WEBHOOK_SECRET
- [ ] Đã cấu hình CASSO_API_KEY và CASSO_SECURE_TOKEN
- [ ] Đã cấu hình IP whitelist
- [ ] Đã tắt PAYMENT_DEBUG
- [ ] Đã phân quyền thư mục đúng
- [ ] Đã backup database
- [ ] Đã thiết lập cron job
- [ ] Đã test trên môi trường staging

## Troubleshooting

### Lỗi: "Database connection failed"
**Giải pháp:**
- Kiểm tra thông tin trong `db.php`
- Kiểm tra MySQL service: `systemctl status mysql`
- Kiểm tra firewall

### Lỗi: "Access denied" khi gọi webhook
**Giải pháp:**
- Kiểm tra ALLOWED_IPS trong `payment_config.php`
- Thêm IP của Casso: 103.146.23.96-98
- Hoặc để trống `[]` để cho phép tất cả (không khuyến khích)

### Lỗi: "Transaction not found"
**Giải pháp:**
- User ghi sai mã giao dịch
- Kiểm tra regex trong `extractUniqueCode()`
- Xem log để debug: `tail -f logs/payment_webhook.log`

### Webhook không được gọi
**Giải pháp:**
- Kiểm tra URL webhook đã đúng chưa
- Kiểm tra SSL certificate (phải HTTPS)
- Test webhook trong Casso dashboard
- Kiểm tra firewall có chặn IP Casso không

### Log file không ghi
**Giải pháp:**
```bash
# Kiểm tra quyền
ls -la logs/
# Phải là: drwxr-xr-x www-data www-data

# Fix quyền
chmod 755 logs/
chown www-data:www-data logs/
```

## Hỗ trợ

Nếu gặp vấn đề:

1. **Xem log chi tiết:**
   ```bash
   tail -100 logs/payment_webhook.log
   ```

2. **Bật debug mode:**
   ```php
   define('PAYMENT_DEBUG', true);
   ```

3. **Liên hệ:**
   - Email: admin@vpnvietnam.com
   - Hotline: 0812.363.898

## Tài liệu tham khảo

- [Hướng dẫn sử dụng](HUONG_DAN_THANH_TOAN_TU_DONG.md)
- [README](README.md)
- [Casso API Documentation](https://docs.casso.vn)

---

**Chúc bạn triển khai thành công! 🎉**
