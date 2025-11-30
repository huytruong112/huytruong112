# ❓ FAQ - Câu Hỏi Thường Gặp

## 🔧 Cài Đặt & Cấu Hình

### Q1: File nào tôi cần chỉnh sửa khi cài đặt?

**A:** Bạn cần chỉnh sửa 2 file:

1. **`config_payment.php`** - Cấu hình webhook
   - Thay đổi `WEBHOOK_SECRET_KEY`
   - Thêm IP vào `ALLOWED_IPS`
   - Bật/tắt `CHECK_IP_WHITELIST`

2. **`db.php`** - Cấu hình database
   - Copy từ `example_db.php`
   - Điền thông tin DB của bạn

### Q2: Tôi có cần thư viện gì không?

**A:** Không cần! Hệ thống chỉ dùng PHP native với các extension:
- `mysqli` (database)
- `json` (JSON parsing)
- `curl` (optional, cho testing)

### Q3: Database cần những bảng nào?

**A:** Chạy file `database_schema.sql` để tạo:
- `users` - Tài khoản người dùng
- `transactions` - Giao dịch
- `webhook_logs` - Log webhook (optional)
- `user_services` - Gói dịch vụ đã mua
- `service_packages` - Danh sách gói
- `receiving_accounts` - TK ngân hàng nhận tiền

### Q4: Tôi đang dùng PostgreSQL, có được không?

**A:** Được! Bạn cần:
1. Thay `mysqli` bằng `PDO` hoặc `pg_*` functions
2. Điều chỉnh SQL syntax (ví dụ: `NOW()` → `CURRENT_TIMESTAMP`)
3. Thay đổi các prepared statements

---

## 🐛 Xử Lý Lỗi

### Q5: Webhook không được gọi, làm sao biết?

**A:** Kiểm tra theo thứ tự:

1. **Check logs:**
   ```bash
   tail -f logs/payment_webhook.log
   ```

2. **Test manual:**
   ```bash
   curl -X POST https://yourdomain.com/api_payment_webhook.php \
     -H "Content-Type: application/json" \
     -d '{"amount": 100000, "description": "TS12345"}'
   ```

3. **Check service dashboard:**
   - Casso: Xem "Lịch sử webhook"
   - VietQR: Xem "Webhook logs"

4. **Check server logs:**
   ```bash
   tail -f /var/log/nginx/error.log
   tail -f /var/log/apache2/error.log
   ```

### Q6: Lỗi "Cannot connect to database"?

**A:** Kiểm tra:
1. File `db.php` có đúng thông tin?
2. MySQL service có chạy không?
   ```bash
   sudo systemctl status mysql
   ```
3. User có quyền truy cập DB không?
   ```sql
   GRANT ALL ON database.* TO 'user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Q7: Lỗi "Permission denied" khi ghi log?

**A:** Fix quyền:
```bash
mkdir -p logs
chmod 755 logs
chown www-data:www-data logs
```

Hoặc đổi owner sang user PHP:
```bash
# Xem user PHP đang chạy
ps aux | grep php

# Thay đổi owner
chown -R php-user:php-group logs/
```

### Q8: Webhook trả về 403 Forbidden?

**A:** Có 2 nguyên nhân:

1. **IP không trong whitelist:**
   ```php
   // Tắt tạm để test
   define('CHECK_IP_WHITELIST', false);
   ```

2. **SSL chưa cài (HTTPS required):**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

### Q9: Số dư không tự động cập nhật?

**A:** Kiểm tra:

1. **Transaction status:**
   ```sql
   SELECT * FROM transactions WHERE unique_code = 'TS12345';
   ```
   
   - Status phải là `success`
   - Nếu vẫn `pending`, webhook chưa xử lý

2. **User balance:**
   ```sql
   SELECT balance FROM users WHERE id = ?;
   ```

3. **Log webhook:**
   ```bash
   grep "TS12345" logs/payment_webhook.log
   ```

4. **Auto-refresh JS:**
   - Mở DevTools → Console
   - Xem có lỗi JS không

---

## 🔒 Bảo Mật

### Q10: Có cần dùng HTTPS không?

**A:** **Bắt buộc!** Các service webhook chỉ gọi HTTPS. Cài SSL:
```bash
# Let's Encrypt (miễn phí)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Q11: Secret key có quan trọng không?

**A:** **Rất quan trọng!** Nó dùng để verify webhook. Nên:
- Dùng random string dài (32+ ký tự)
- Không commit lên Git
- Thay đổi định kỳ (3-6 tháng)

Tạo secret key:
```bash
# Linux/Mac
openssl rand -base64 32

# Hoặc
head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32
```

### Q12: IP Whitelist có cần thiết không?

**A:** **Nên bật** trong production để chặn request giả mạo:

```php
define('CHECK_IP_WHITELIST', true);
define('ALLOWED_IPS', [
    '103.xxx.xxx.xxx', // IP thật của service
]);
```

Lấy IP từ:
- **Casso:** Hỏi support hoặc xem docs
- **VietQR:** Trong dashboard
- **Sepay:** Trong cài đặt API

### Q13: Có cách nào chống brute force không?

**A:** Có! Thêm rate limiting:

```php
// Trong api_payment_webhook.php
function check_rate_limit(): bool {
    $ip = $_SERVER['REMOTE_ADDR'];
    $file = "/tmp/webhook_rate_{$ip}.txt";
    
    $count = file_exists($file) ? (int)file_get_contents($file) : 0;
    if ($count > 100) return false; // Max 100 requests/phút
    
    file_put_contents($file, $count + 1);
    
    // Auto cleanup sau 60s
    if ($count === 0) {
        sleep(60);
        @unlink($file);
    }
    
    return true;
}
```

---

## 💡 Tính Năng

### Q14: Có thể dùng nhiều tài khoản ngân hàng không?

**A:** Được! Thêm vào bảng `receiving_accounts`:

```sql
INSERT INTO receiving_accounts (bank_name, account_number, account_holder, status)
VALUES 
    ('VPBank', '1234567890', 'NGUYEN VAN A', 'active'),
    ('Techcombank', '9876543210', 'NGUYEN VAN A', 'active');
```

Sau đó điều chỉnh logic hiển thị trong `deposit.php`.

### Q15: Có thể gửi email thông báo khi nạp tiền thành công không?

**A:** Được! Thêm vào `api_payment_webhook.php`:

```php
// Sau khi process_payment thành công
if ($result['success']) {
    $user_email = get_user_email($user_id);
    send_payment_notification_email($user_email, $amount, $unique_code);
}

function send_payment_notification_email($to, $amount, $code) {
    $subject = "Nạp tiền thành công - " . number_format($amount) . " VND";
    $message = "Giao dịch {$code} đã được xác nhận. Số tiền: " . number_format($amount) . " VND";
    mail($to, $subject, $message, "From: noreply@yourdomain.com");
}
```

### Q16: Có thể tự động hoàn tiền nếu chuyển sai số tiền không?

**A:** Có thể! Thêm logic:

```php
// Trong process_payment()
if (abs($amount - $expected_amount) > 1000) {
    // Nếu chuyển NHIỀU hơn → Cộng số tiền thừa vào balance
    if ($amount > $expected_amount) {
        $excess = $amount - $expected_amount;
        // Update balance += $amount (cả số tiền chuyển)
        // Ghi chú: "Đã cộng {$excess} VND thừa vào tài khoản"
    }
    // Nếu chuyển ÍT hơn → Yêu cầu chuyển thêm
    else {
        return ['success' => false, 'message' => 'Thiếu tiền'];
    }
}
```

### Q17: Có thể tích hợp với Telegram bot không?

**A:** Được! Tạo bot và thêm:

```php
function send_telegram_notification($message) {
    $bot_token = 'YOUR_BOT_TOKEN';
    $chat_id = 'YOUR_CHAT_ID';
    
    $url = "https://api.telegram.org/bot{$bot_token}/sendMessage";
    file_get_contents($url . '?' . http_build_query([
        'chat_id' => $chat_id,
        'text' => $message,
        'parse_mode' => 'HTML'
    ]));
}

// Gọi khi có payment
send_telegram_notification("💰 <b>Nạp tiền mới!</b>\nUser: {$user_id}\nSố tiền: " . number_format($amount) . " VND");
```

---

## 🧪 Testing

### Q18: Làm sao test mà không cần chuyển tiền thật?

**A:** Dùng test script:

1. Tạo transaction test:
   ```bash
   php create_test_transaction.php
   ```

2. Test webhook:
   ```bash
   php test_webhook.php
   ```

3. Hoặc curl:
   ```bash
   curl -X POST http://localhost/api_payment_webhook.php \
     -H "Content-Type: application/json" \
     -d '{"amount": 100000, "description": "TS12345"}'
   ```

### Q19: Postman collection có sẵn không?

**A:** Có! Import file `postman_collection.json` (trong INTEGRATION_GUIDE.md)

### Q20: Có công cụ nào giả lập webhook của Casso/VietQR không?

**A:** Có! Dùng [webhook.site](https://webhook.site):

1. Vào https://webhook.site
2. Copy URL unique
3. Cấu hình trong Casso/VietQR
4. Xem request thật → Copy payload
5. Gửi đến server của bạn để test

---

## 📊 Performance

### Q21: Webhook có bị chậm không?

**A:** Không! Thời gian xử lý trung bình: **< 100ms**

- Parse JSON: ~5ms
- Query DB: ~20ms
- Update transaction: ~30ms
- Update balance: ~20ms
- Log: ~10ms

### Q22: Có thể xử lý bao nhiêu request/giây?

**A:** Phụ thuộc server, nhưng thường:
- VPS nhỏ (1 core, 1GB RAM): ~50 req/s
- VPS trung bình (2 core, 2GB RAM): ~200 req/s
- VPS lớn (4+ core, 4GB+ RAM): ~500+ req/s

Tối ưu:
- Dùng Redis cache
- Index DB đúng cột
- Bật opcache PHP

### Q23: Log có tốn nhiều dung lượng không?

**A:** Không nhiều. Ước tính:
- 1 request = ~500 bytes log
- 1000 requests/ngày = ~500KB/ngày = ~15MB/tháng

Auto cleanup:
```bash
# Cron job xóa log cũ hơn 30 ngày
0 0 * * * find /path/to/logs -name "*.log" -mtime +30 -delete
```

---

## 🚀 Deploy & Production

### Q24: Nên deploy trên hosting nào?

**A:** Khuyến nghị:

- **VPS:** DigitalOcean, Linode, Vultr, AWS EC2
- **Shared hosting:** Hostinger, SiteGround (nếu hỗ trợ webhook)
- **Cloud:** AWS Lambda, Google Cloud Functions (cần điều chỉnh code)

### Q25: Cần cấu hình gì trên server production?

**A:** Checklist:

```bash
# 1. Install dependencies
sudo apt update
sudo apt install php php-mysqli php-curl php-json nginx certbot

# 2. Cấu hình PHP
sudo nano /etc/php/8.1/fpm/php.ini
# Tăng:
# max_execution_time = 300
# memory_limit = 256M

# 3. Cấu hình Nginx
sudo nano /etc/nginx/sites-available/default
# Add location block cho webhook

# 4. SSL
sudo certbot --nginx -d yourdomain.com

# 5. Permissions
sudo chown -R www-data:www-data /var/www/html
chmod 755 /var/www/html
chmod 755 logs/

# 6. Firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 7. Restart
sudo systemctl restart nginx php8.1-fpm
```

### Q26: Có cần backup không?

**A:** **Cần!** Setup auto backup:

```bash
#!/bin/bash
# /opt/backup_webhook.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/webhook"

# Backup database
mysqldump -u user -p'password' database > "$BACKUP_DIR/db_$DATE.sql"

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" /var/www/html/logs/

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Cron:
```bash
0 2 * * * /opt/backup_webhook.sh
```

---

## 💰 Chi Phí

### Q27: Tổng chi phí là bao nhiêu?

**A:** Ước tính:

| Item | Chi phí |
|------|---------|
| VPS | 100k-500k/tháng |
| Domain | 200k/năm |
| SSL | Free (Let's Encrypt) |
| Casso/Sepay | 200k-300k/tháng |
| **Tổng** | **~400k-800k/tháng** |

### Q28: Có giải pháp nào rẻ hơn không?

**A:** Có:
- **Shared hosting:** ~50k/tháng (nhưng giới hạn)
- **Email parsing:** Free (nhưng delay)
- **Manual confirm:** Free (nhưng mất thời gian)

---

## 📞 Hỗ Trợ

### Q29: Tôi gặp lỗi không có trong FAQ, làm sao?

**A:** Liên hệ:
- Email: support.vpn@vpnvietnam.com
- Hotline: 0826.003.926
- Hoặc tạo issue trên GitHub

### Q30: Có hỗ trợ custom không?

**A:** Có! Chúng tôi hỗ trợ:
- Setup hệ thống
- Tích hợp custom
- Fix bugs
- Tối ưu hiệu suất

Liên hệ qua email để báo giá.

---

**Cập nhật lần cuối: 2025-01-01**
