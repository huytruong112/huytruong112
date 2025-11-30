# 🚀 Hướng Dẫn Cài Đặt & Test Webhook Thanh Toán

## 📋 Yêu Cầu

- PHP 7.4+
- MySQL/MariaDB
- Extension: mysqli, curl, json
- SSL Certificate (cho production)

## 🔧 Cài Đặt Nhanh (5 phút)

### Bước 1: Copy file config

```bash
cp example_config_payment.php config_payment.php
```

Mở `config_payment.php` và chỉnh sửa:

```php
// Thay đổi secret key
define('WEBHOOK_SECRET_KEY', 'your-random-secret-key-here');

// Thêm IP của service webhook (production)
define('ALLOWED_IPS', [
    '103.xxx.xxx.xxx', // IP thật của Casso/VietQR
]);

// Tắt check IP khi test local
define('CHECK_IP_WHITELIST', false);
```

### Bước 2: Tạo thư mục logs

```bash
mkdir -p logs
chmod 755 logs
```

### Bước 3: Kiểm tra database

Đảm bảo bảng `transactions` có các cột:
- `transaction_id` (PK)
- `user_id`
- `amount_paid`
- `unique_code`
- `status` (varchar: 'pending', 'success', 'failed')
- `transaction_date`
- `description`

Đảm bảo bảng `users` có cột `balance`.

### Bước 4: Test local

#### 4.1. Tạo giao dịch test:

```bash
php create_test_transaction.php
```

Output mong đợi:
```
=================================
  TẠO GIAO DỊCH TEST
=================================

User ID: 1 (admin)

Tạo 5 giao dịch test...

✅ TS12345: Tạo thành công (Số tiền: 100,000 VND)
✅ TS67890: Tạo thành công (Số tiền: 50,000 VND)
...
```

#### 4.2. Test webhook:

```bash
php test_webhook.php
```

Hoặc dùng curl:

```bash
curl -X POST http://localhost/api_payment_webhook.php \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST001",
    "amount": 100000,
    "description": "TS12345 Nap tien test"
  }'
```

#### 4.3. Kiểm tra logs:

```bash
tail -f logs/payment_webhook.log
```

### Bước 5: Deploy lên server

#### 5.1. Upload files:

```bash
scp -r *.php config_payment.php user@server:/var/www/html/
```

#### 5.2. Set permissions:

```bash
ssh user@server
cd /var/www/html
chmod 755 *.php
chmod 755 logs/
chown -R www-data:www-data logs/
```

#### 5.3. Cấu hình SSL (bắt buộc cho webhook):

```bash
# Sử dụng Let's Encrypt (miễn phí)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### 5.4. Bật IP whitelist:

Mở `config_payment.php`:

```php
define('CHECK_IP_WHITELIST', true);
define('ALLOWED_IPS', [
    '103.xxx.xxx.xxx', // IP thật từ service provider
]);
```

### Bước 6: Cấu hình webhook tại service provider

#### Option A: Casso.vn

1. Đăng nhập [https://casso.vn](https://casso.vn)
2. **Tài khoản** → **Cài đặt** → **Webhook**
3. Nhập URL: `https://yourdomain.com/api_payment_webhook.php`
4. Chọn sự kiện: **Có giao dịch mới**
5. **Test webhook** → **Lưu**

#### Option B: VietQR.io

1. Đăng ký tài khoản tại [https://vietqr.io](https://vietqr.io)
2. Tạo API key
3. Cấu hình webhook URL
4. Lưu và test

#### Option C: Banking API khác

Làm theo hướng dẫn của từng service.

### Bước 7: Test production

#### 7.1. Tạo giao dịch thật:

1. Đăng nhập vào hệ thống
2. Vào trang **Nạp tiền**
3. Nhập số tiền (ví dụ: 50,000 VND)
4. Hệ thống tạo mã (ví dụ: `TS12345`)

#### 7.2. Chuyển khoản test:

Chuyển **50,000 VND** vào tài khoản ngân hàng với nội dung:

```
TS12345
```

hoặc

```
TS12345 Nap tien test
```

#### 7.3. Kiểm tra:

- Sau vài giây, số dư tài khoản sẽ tự động cộng thêm 50,000
- Trạng thái giao dịch chuyển từ "Chờ xử lý" → "Đã thanh toán"

#### 7.4. Xem logs:

```bash
ssh user@server
tail -f /var/www/html/logs/payment_webhook.log
```

## 🧪 Test Cases

### Test 1: Mã chuẩn
- Nội dung: `TS12345`
- Kết quả: ✅ Pass

### Test 2: Mã viết thường
- Nội dung: `ts12345`
- Kết quả: ✅ Pass

### Test 3: Mã có khoảng trắng
- Nội dung: `TS 12345`
- Kết quả: ✅ Pass

### Test 4: Mã trong câu dài
- Nội dung: `Chuyen tien TS12345 cho tai khoan`
- Kết quả: ✅ Pass

### Test 5: Không có mã
- Nội dung: `Chuyen tien khong co ma`
- Kết quả: ❌ Fail (mong đợi)

### Test 6: Số tiền không khớp
- Mong đợi: 100,000 VND
- Thực tế: 50,000 VND
- Kết quả: ❌ Fail (mong đợi)

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi 1: "Cannot connect to database"

**Nguyên nhân:** File `db.php` chưa cấu hình đúng

**Giải pháp:**
```php
// Mở db.php và kiểm tra
$conn = new mysqli('localhost', 'username', 'password', 'database');
```

### Lỗi 2: "Permission denied" khi ghi log

**Nguyên nhân:** Thư mục logs không có quyền ghi

**Giải pháp:**
```bash
chmod 755 logs/
chown www-data:www-data logs/
```

### Lỗi 3: Webhook không được gọi

**Nguyên nhân:** URL không đúng hoặc SSL chưa cài

**Giải pháp:**
- Kiểm tra URL: `https://yourdomain.com/api_payment_webhook.php`
- Cài SSL certificate
- Test bằng curl từ máy khác

### Lỗi 4: "Invalid signature"

**Nguyên nhân:** Secret key không khớp

**Giải pháp:**
- Kiểm tra secret key trong config
- Hoặc tạm tắt signature check khi test:
  ```php
  // Comment dòng này trong api_payment_webhook.php
  // if (!verify_webhook_signature($payload)) { ... }
  ```

### Lỗi 5: "IP Forbidden"

**Nguyên nhân:** IP không trong whitelist

**Giải pháp:**
```php
// Tắt check IP khi test
define('CHECK_IP_WHITELIST', false);

// Hoặc thêm IP vào whitelist
define('ALLOWED_IPS', ['xxx.xxx.xxx.xxx']);
```

## 📊 Monitoring

### Xem log realtime:

```bash
tail -f logs/payment_webhook.log
```

### Xem log có filter:

```bash
# Chỉ xem SUCCESS
grep "SUCCESS" logs/payment_webhook.log

# Chỉ xem ERROR
grep "ERROR" logs/payment_webhook.log

# Xem log hôm nay
grep "$(date '+%Y-%m-%d')" logs/payment_webhook.log
```

### Kiểm tra database:

```sql
-- Xem giao dịch pending
SELECT * FROM transactions WHERE status = 'pending' ORDER BY transaction_date DESC;

-- Xem giao dịch hôm nay
SELECT * FROM transactions WHERE DATE(transaction_date) = CURDATE();

-- Xem tổng tiền đã nạp
SELECT SUM(amount_paid) as total FROM transactions WHERE status = 'success';
```

## 🔐 Security Checklist

- [ ] Đã thay đổi `WEBHOOK_SECRET_KEY`
- [ ] Đã bật `CHECK_IP_WHITELIST = true` (production)
- [ ] Đã cài SSL certificate (HTTPS)
- [ ] Đã test signature verification
- [ ] File `config_payment.php` không bị commit lên Git
- [ ] Database có index cho `unique_code`
- [ ] Đã set quyền file đúng (755)
- [ ] Logs không public (đặt ngoài web root hoặc deny access)

## 📞 Support

- **Email:** support.vpn@vpnvietnam.com
- **Hotline:** 0826.003.926
- **Docs:** README_PAYMENT_WEBHOOK.md

## 🎉 Hoàn Thành!

Hệ thống webhook đã sẵn sàng. Khi có chuyển khoản thành công:

1. ✅ Webhook tự động nhận thông báo
2. ✅ Parse mã giao dịch (TS12345)
3. ✅ Cập nhật status → success
4. ✅ Cộng tiền vào balance
5. ✅ Ghi log

**Chúc bạn thành công! 🚀**
