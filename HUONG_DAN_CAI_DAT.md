# HƯỚNG DẪN CÀI ĐẶT NHANH

## Giới Thiệu

Hệ thống API thanh toán tự động giúp bạn tự động xác nhận giao dịch nạp tiền khi khách hàng chuyển khoản ngân hàng.

## Cách 1: Sử Dụng Casso.vn (KHUYẾN NGHỊ - DỄ NHẤT)

### Ưu điểm:
- ✅ Không cần reverse engineer API ngân hàng
- ✅ Hợp pháp, không vi phạm ToS ngân hàng
- ✅ Hỗ trợ webhook realtime
- ✅ Hỗ trợ nhiều ngân hàng VN
- ✅ Ổn định, bảo trì tốt

### Bước 1: Đăng ký Casso

1. Truy cập: https://casso.vn
2. Đăng ký tài khoản (miễn phí 7 ngày trial)
3. Liên kết tài khoản ngân hàng của bạn
4. Lấy API Key tại: https://casso.vn/user/setting/keys

### Bước 2: Cấu hình

Mở file `payment_config.php`:

```php
// Bật sử dụng Casso
define('USE_COMMUNITY_API', true);
define('COMMUNITY_API_URL', 'https://oauth.casso.vn/v2');
define('COMMUNITY_API_KEY', 'your-casso-api-key-here');

// Bật auto check
define('PAYMENT_AUTO_CHECK_ENABLED', true);

// Đổi secret keys
define('WEBHOOK_SECRET', 'your-random-secret-key-123456');
define('PAYMENT_API_SECRET', 'your-random-api-secret-key-789');
```

### Bước 3: Cài đặt Database

```bash
mysql -u username -p database_name < db_schema.sql
```

Hoặc chạy SQL thủ công:

```sql
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NULL DEFAULT NULL;
```

### Bước 4: Cài đặt Cronjob

Sửa cronjob để dùng version Casso:

```bash
crontab -e
```

Thêm dòng (thay đổi đường dẫn cho đúng):

```bash
*/1 * * * * /usr/bin/php /path/to/your/project/cron_check_payment_casso.php >> /path/to/your/project/logs/cron.log 2>&1
```

### Bước 5: Tạo file cronjob cho Casso

Tạo file `cron_check_payment_casso.php`:

```php
#!/usr/bin/env php
<?php
if (php_sapi_name() !== 'cli') {
    die('This script must be run from command line');
}

require_once __DIR__ . '/db.php';
require_once __DIR__ . '/auto_payment_check_casso.php';

$processor = new AutoPaymentProcessorCasso($conn);
$processor->process();
?>
```

Phân quyền:

```bash
chmod +x cron_check_payment_casso.php
```

### Bước 6: Cấu hình Webhook (Optional - Realtime)

1. Vào Casso Dashboard: https://casso.vn/dashboard
2. Chọn "Webhook" trong menu
3. Nhập URL webhook: `https://yourdomain.com/webhook_payment_casso.php`
4. Chọn "Tiền vào" (income)
5. Save

Webhook sẽ gửi thông báo realtime mỗi khi có giao dịch mới, không cần đợi cronjob.

### Bước 7: Test

```bash
# Test cronjob
php cron_check_payment_casso.php

# Xem log
tail -f logs/payment.log
tail -f logs/cron.log
```

### Bước 8: Tạo giao dịch test

1. Đăng nhập vào hệ thống
2. Vào trang nạp tiền
3. Nhập số tiền (VD: 10,000 VND)
4. Click "Nạp tiền"
5. Copy mã giao dịch (VD: TS12345)
6. Chuyển khoản vào tài khoản ngân hàng với nội dung: **TS12345**
7. Đợi 1-2 phút (cronjob chạy)
8. Số dư sẽ tự động cập nhật

---

## Cách 2: Kết Nối Trực Tiếp API Ngân Hàng (KHUYÊN KHÔNG NÊN)

### Nhược điểm:
- ❌ Phức tạp, cần reverse engineer
- ❌ Có thể vi phạm ToS ngân hàng
- ❌ API có thể thay đổi bất cứ lúc nào
- ❌ Cần xử lý captcha, 2FA
- ❌ Rủi ro bảo mật cao

Nếu vẫn muốn làm, xem file `README_PAYMENT_API.md` để biết chi tiết.

---

## Cách 3: Sử Dụng Payment Gateway Khác

### VNPay

- URL: https://vnpay.vn
- Hỗ trợ: Thanh toán QR, thẻ, ví điện tử
- Phí: 1.5-2% mỗi giao dịch

### MoMo

- URL: https://business.momo.vn
- Hỗ trợ: Ví MoMo, QR code
- Phí: 1.5% mỗi giao dịch

### ZaloPay

- URL: https://zalopay.vn/business
- Hỗ trợ: Ví ZaloPay, QR code
- Phí: 1.5% mỗi giao dịch

---

## Troubleshooting

### Cronjob không chạy

```bash
# Check xem cronjob có được thêm chưa
crontab -l

# Check log cronjob hệ thống
grep CRON /var/log/syslog

# Test chạy thủ công
php cron_check_payment_casso.php
```

### Không kết nối được Casso

- Check API Key có đúng không
- Check tài khoản Casso còn hạn không (trial 7 ngày)
- Check log: `tail -f logs/payment.log`
- Test API bằng curl:

```bash
curl -H "Authorization: Apikey YOUR_API_KEY" \
  "https://oauth.casso.vn/v2/transactions?fromDate=1609459200000&toDate=1640995200000"
```

### Giao dịch không tự động xác nhận

1. **Check cronjob có chạy không**:
   ```bash
   tail -f logs/cron.log
   ```

2. **Check log payment**:
   ```bash
   tail -f logs/payment.log
   ```

3. **Check database**:
   ```sql
   SELECT * FROM transactions WHERE unique_code = 'TS12345';
   ```

4. **Check nội dung chuyển khoản**:
   - Phải đúng mã (VD: TS12345)
   - Không có khoảng trắng thừa
   - Không có ký tự đặc biệt

5. **Check số tiền**:
   - Phải khớp chính xác

### Webhook không hoạt động

1. **Check URL webhook**:
   - Phải là HTTPS
   - Phải accessible từ internet

2. **Test webhook bằng curl**:
   ```bash
   curl -X POST https://yourdomain.com/webhook_payment_casso.php \
     -H "Content-Type: application/json" \
     -d '{"data":{"id":"123","amount":10000,"description":"TS12345 Nap tien","when":1640995200000}}'
   ```

3. **Check log webhook**:
   ```bash
   tail -f logs/payment.log | grep Webhook
   ```

---

## Bảo Mật

### Quan Trọng

1. **Đổi secret keys** trong `payment_config.php`
2. **Không commit** `payment_config.php` lên git
3. **Sử dụng HTTPS** cho tất cả endpoints
4. **Giới hạn IP** cho webhook (whitelist Casso IPs)
5. **Backup database** thường xuyên

### Whitelist Casso IPs

Trong Apache/Nginx config:

```nginx
# Nginx
location /webhook_payment_casso.php {
    allow 172.105.162.113;
    allow 139.162.29.153;
    deny all;
}
```

```apache
# Apache
<Location /webhook_payment_casso.php>
    Require ip 172.105.162.113
    Require ip 139.162.29.153
</Location>
```

---

## Giá Casso.vn

- **Trial**: 7 ngày miễn phí
- **Starter**: 299,000 VND/tháng (5,000 giao dịch)
- **Business**: 599,000 VND/tháng (20,000 giao dịch)
- **Enterprise**: Liên hệ

Chi tiết: https://casso.vn/pricing

---

## Support

- **Email**: support@yourdomain.com
- **Hotline**: 0812.363.898
- **Casso Support**: support@casso.vn

---

## Checklist Cài Đặt

- [ ] Đăng ký Casso.vn
- [ ] Liên kết tài khoản ngân hàng
- [ ] Lấy API Key
- [ ] Cấu hình `payment_config.php`
- [ ] Chạy `db_schema.sql`
- [ ] Tạo file `cron_check_payment_casso.php`
- [ ] Thêm cronjob
- [ ] Cấu hình webhook (optional)
- [ ] Test giao dịch
- [ ] Check log
- [ ] Đổi secret keys
- [ ] Backup database

---

Chúc bạn thành công! 🎉
