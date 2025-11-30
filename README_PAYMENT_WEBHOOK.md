# 🔔 Hệ thống Webhook Thanh Toán Tự Động

## 📋 Mô tả

Hệ thống này tự động xác nhận và xử lý thanh toán khi khách hàng chuyển khoản thành công vào tài khoản ngân hàng.

## 🏗️ Cấu trúc File

```
├── config_payment.php              # Cấu hình webhook (secret key, IP whitelist)
├── api_payment_webhook.php         # API webhook chính nhận thông báo từ ngân hàng
├── check_transaction_status.php    # API kiểm tra trạng thái giao dịch (AJAX)
├── check_balance.php               # API kiểm tra số dư (AJAX)
└── logs/
    └── payment_webhook.log         # Log file (tự động tạo)
```

## ⚙️ Cách Hoạt Động

### Flow thanh toán:

1. **Khách hàng tạo lệnh nạp tiền:**
   - Vào trang `deposit.php`
   - Nhập số tiền → Hệ thống tạo mã giao dịch (ví dụ: `TS12345`)
   - Trạng thái: `pending`

2. **Khách hàng chuyển khoản:**
   - Chuyển đúng số tiền vào tài khoản ngân hàng
   - Nội dung CK: `TS12345` (hoặc `TS 12345`, `ts12345`)

3. **Ngân hàng gửi webhook:**
   - Service (Casso/VietQR/etc.) nhận biến động số dư
   - Gửi POST request đến `api_payment_webhook.php`

4. **Hệ thống tự động xử lý:**
   - Parse nội dung CK → tìm mã `TS12345`
   - Tìm giao dịch `pending` tương ứng
   - Kiểm tra số tiền khớp
   - Cập nhật trạng thái: `pending` → `success`
   - Cộng tiền vào `users.balance`

5. **Khách hàng nhận tiền:**
   - Trang `deposit.php` tự động refresh số dư mỗi 10s
   - Hoặc click "Xem lại trạng thái" để kiểm tra ngay

## 🔧 Cài Đặt

### 1. Cấu hình Webhook

Mở file `config_payment.php` và chỉnh sửa:

```php
// Thay đổi secret key (bắt buộc!)
define('WEBHOOK_SECRET_KEY', 'your-secret-key-here-change-in-production');

// Thêm IP của service webhook vào whitelist (khuyến nghị)
define('ALLOWED_IPS', [
    '103.123.456.789', // IP của Casso/VietQR
]);

// Bật kiểm tra IP khi production
define('CHECK_IP_WHITELIST', true);
```

### 2. Tạo thư mục logs

```bash
mkdir -p logs
chmod 755 logs
```

### 3. Cấu hình Service Webhook

Tùy service bạn dùng:

#### A. Casso.vn

1. Đăng nhập [Casso.vn](https://casso.vn)
2. Vào **Cài đặt** → **Webhook**
3. Nhập URL: `https://yourdomain.com/api_payment_webhook.php`
4. Chọn sự kiện: **Có giao dịch mới**
5. Lưu

#### B. VietQR

1. Đăng ký API tại [VietQR.io](https://vietqr.io)
2. Cấu hình webhook URL
3. Nhận API key

#### C. Banking API trực tiếp

Liên hệ ngân hàng để đăng ký webhook hoặc dùng service trung gian.

### 4. Test Webhook

#### Test bằng curl:

```bash
curl -X POST https://yourdomain.com/api_payment_webhook.php \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST123",
    "amount": 100000,
    "description": "TS12345 Nap tien",
    "date": "2024-01-01 10:00:00"
  }'
```

#### Test bằng Postman:

1. Method: `POST`
2. URL: `https://yourdomain.com/api_payment_webhook.php`
3. Body (JSON):
   ```json
   {
     "transaction_id": "TEST123",
     "amount": 100000,
     "description": "TS12345 Nap tien",
     "date": "2024-01-01 10:00:00"
   }
   ```

## 📊 Format Payload

### Casso Format:
```json
{
  "id": 123456,
  "tid": "FT21123456789",
  "description": "TS12345 Nap tien",
  "amount": 100000,
  "when": "2024-01-01 10:00:00",
  "bank_sub_acc_id": "12345"
}
```

### VietQR Format:
```json
{
  "transaction_id": "ABC123",
  "amount": 100000,
  "content": "TS12345",
  "date": "2024-01-01 10:00:00"
}
```

### Custom Format:
API hỗ trợ nhiều format, chỉ cần có:
- `amount`: Số tiền
- `description` hoặc `content`: Nội dung CK (chứa mã TS12345)
- `transaction_id` hoặc `id`: Mã giao dịch ngân hàng

## 🔒 Bảo Mật

### 1. Secret Key
- Thay đổi `WEBHOOK_SECRET_KEY` trong production
- Không commit secret key lên Git

### 2. IP Whitelist
- Chỉ cho phép IP của service webhook
- Bật `CHECK_IP_WHITELIST = true`

### 3. Signature Verification
- Uncomment dòng này trong `api_payment_webhook.php`:
  ```php
  if (!verify_webhook_signature($payload)) {
      json_response(['success' => false, 'message' => 'Invalid signature'], 401);
  }
  ```
- Điều chỉnh logic verify theo service bạn dùng

### 4. HTTPS
- Bắt buộc dùng HTTPS cho webhook URL
- Cài SSL certificate (Let's Encrypt miễn phí)

## 📝 Logs

### Xem logs:
```bash
tail -f logs/payment_webhook.log
```

### Format log:
```
[2024-01-01 10:00:00] [INFO] Payment processed successfully: user_id=123, amount=100000, code=TS12345
[2024-01-01 10:01:00] [WARNING] Cannot extract unique_code from: abc xyz
[2024-01-01 10:02:00] [ERROR] Amount mismatch: expected=100000, received=50000
```

### Levels:
- `DEBUG`: Chi tiết request/response (khi WEBHOOK_DEBUG=true)
- `INFO`: Thông tin thông thường
- `WARNING`: Cảnh báo (không ảnh hưởng)
- `ERROR`: Lỗi xử lý
- `FATAL`: Lỗi nghiêm trọng

## 🧪 Testing

### 1. Test flow hoàn chỉnh:

1. Tạo giao dịch test:
   ```sql
   INSERT INTO transactions (user_id, amount_paid, unique_code, status, transaction_date)
   VALUES (1, 100000, 'TS12345', 'pending', NOW());
   ```

2. Gửi webhook:
   ```bash
   curl -X POST http://localhost/api_payment_webhook.php \
     -H "Content-Type: application/json" \
     -d '{"amount": 100000, "description": "TS12345 Test"}'
   ```

3. Kiểm tra DB:
   ```sql
   SELECT * FROM transactions WHERE unique_code = 'TS12345';
   SELECT balance FROM users WHERE id = 1;
   ```

### 2. Test với nhiều format mã:
- `TS12345` ✅
- `ts12345` ✅
- `TS 12345` ✅
- `TS-12345` ✅
- `Nap tien TS12345` ✅
- `TS12345 nap tien cho toi` ✅

## 🐛 Troubleshooting

### Webhook không hoạt động:

1. **Check logs:**
   ```bash
   tail -f logs/payment_webhook.log
   ```

2. **Check permissions:**
   ```bash
   chmod 755 api_payment_webhook.php
   chmod 755 logs/
   ```

3. **Check database connection:**
   - Đảm bảo `db.php` kết nối đúng
   - Test: `php -f db.php`

4. **Check format payload:**
   - Xem log debug để biết format thực tế
   - Điều chỉnh parsing logic nếu cần

### Số dư không cập nhật:

1. Kiểm tra transaction status:
   ```sql
   SELECT * FROM transactions WHERE unique_code = 'TS12345';
   ```

2. Kiểm tra user balance:
   ```sql
   SELECT balance FROM users WHERE id = ?;
   ```

3. Xem log transaction trong DB

### Mã giao dịch không khớp:

- Kiểm tra regex trong `extract_unique_code()`
- Đảm bảo nội dung CK có chứa mã đúng format

## 📞 Hỗ Trợ

- **Email:** support.vpn@vpnvietnam.com
- **Hotline:** 0826.003.926
- **Website:** https://vpnvietnam.com

## 📄 License

© 2025 VPN Vietnam. All rights reserved.
