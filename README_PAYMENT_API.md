# Hệ Thống API Thanh Toán Tự Động

## Tổng Quan

Hệ thống API thanh toán tự động cho phép tự động xác nhận giao dịch nạp tiền khi khách hàng chuyển khoản ngân hàng. Hệ thống sẽ tự động kiểm tra giao dịch từ ngân hàng và cập nhật số dư cho user mà không cần xử lý thủ công.

## Tính Năng

✅ **Tự động kiểm tra giao dịch ngân hàng** - Kết nối API ngân hàng để lấy lịch sử giao dịch  
✅ **So khớp tự động** - So khớp mã giao dịch và số tiền với database  
✅ **Cập nhật số dư tự động** - Tự động cộng tiền vào tài khoản khi xác nhận thành công  
✅ **Webhook hỗ trợ** - Nhận callback realtime từ ngân hàng (nếu có)  
✅ **Cronjob định kỳ** - Kiểm tra tự động mỗi phút  
✅ **Hủy giao dịch quá hạn** - Tự động hủy giao dịch pending quá 24h  
✅ **Logging đầy đủ** - Ghi log chi tiết mọi hoạt động  
✅ **Hỗ trợ đa ngân hàng** - VCB, MB Bank, ACB, TPBank, Techcombank, VietinBank  

## Cấu Trúc File

```
/workspace/
├── payment_config.php          # Cấu hình API ngân hàng
├── bank_api_helper.php         # Helper kết nối API ngân hàng
├── auto_payment_check.php      # Script xử lý thanh toán tự động
├── webhook_payment.php         # Webhook nhận callback từ ngân hàng
├── cron_check_payment.php      # Cronjob chạy định kỳ
├── check_transaction_status.php # API check trạng thái giao dịch
├── check_balance.php           # API check số dư
├── transaction_detail.php      # Hiển thị chi tiết giao dịch
└── logs/                       # Thư mục chứa log files
    ├── payment.log
    └── cron.log
```

## Cài Đặt

### Bước 1: Upload Files

Upload tất cả các file vào thư mục web của bạn (cùng thư mục với `deposit.php`)

### Bước 2: Phân Quyền

```bash
# Phân quyền thư mục logs
mkdir -p logs
chmod 755 logs

# Phân quyền file cronjob
chmod +x cron_check_payment.php
```

### Bước 3: Cấu Hình Database

Đảm bảo bảng `transactions` có cột `updated_at`:

```sql
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NULL DEFAULT NULL;
```

### Bước 4: Cấu Hình API Ngân Hàng

Mở file `payment_config.php` và cấu hình:

```php
// Chọn loại ngân hàng
define('BANK_API_TYPE', 'vcb'); // vcb, mbbank, acb, tpbank, etc.

// Điền thông tin đăng nhập ngân hàng
define('VCB_USERNAME', 'your_username');
define('VCB_PASSWORD', 'your_password');
define('VCB_ACCOUNT_NUMBER', 'your_account_number');

// Bật auto check
define('PAYMENT_AUTO_CHECK_ENABLED', true);

// Đổi secret keys
define('WEBHOOK_SECRET', 'your-secure-webhook-secret');
define('PAYMENT_API_SECRET', 'your-secure-api-secret');
```

### Bước 5: Cài Đặt Cronjob

Thêm cronjob để chạy tự động mỗi phút:

```bash
crontab -e
```

Thêm dòng sau:

```bash
*/1 * * * * /usr/bin/php /path/to/your/project/cron_check_payment.php >> /path/to/your/project/logs/cron.log 2>&1
```

**Lưu ý**: Thay `/path/to/your/project/` bằng đường dẫn thực tế đến thư mục project của bạn.

### Bước 6: Kiểm Tra Cronjob

```bash
# Xem log cronjob
tail -f logs/cron.log

# Xem log payment
tail -f logs/payment.log
```

## Cách Hoạt Động

### Flow Thanh Toán Tự Động

1. **User tạo giao dịch nạp tiền**
   - User nhập số tiền muốn nạp
   - Hệ thống tạo transaction với `status = 'pending'` và `unique_code` (VD: TS12345)
   - Hiển thị thông tin chuyển khoản cho user

2. **User chuyển khoản**
   - User chuyển khoản với nội dung chính xác là `unique_code` (VD: TS12345)
   - Số tiền khớp với số tiền yêu cầu

3. **Hệ thống tự động xác nhận**
   - **Cronjob** chạy mỗi phút, gọi `auto_payment_check.php`
   - Lấy danh sách transaction `pending` từ database
   - Gọi API ngân hàng để lấy lịch sử giao dịch 24h gần nhất
   - So khớp `unique_code` và `amount`
   - Nếu khớp:
     - Cập nhật transaction: `status = 'success'`
     - Cộng tiền vào user: `balance = balance + amount`
     - Ghi log

4. **User thấy kết quả**
   - Frontend tự động refresh mỗi 10s để check số dư
   - User có thể click "Xem lại trạng thái" để force check
   - Modal hiển thị chi tiết giao dịch

### Webhook (Optional)

Nếu ngân hàng hỗ trợ webhook/callback:

1. Cấu hình URL webhook: `https://yourdomain.com/webhook_payment.php`
2. Khi có giao dịch mới, ngân hàng sẽ gửi POST request đến webhook
3. Webhook tự động xử lý ngay lập tức (không cần đợi cronjob)

## API Endpoints

### 1. Check Transaction Status

**Endpoint**: `check_transaction_status.php?code=TS12345`

**Response**:
```json
{
  "success": true,
  "status": "success",
  "transaction_id": 123,
  "amount": 100000,
  "date": "2025-11-30 10:30:00",
  "auto_check": true,
  "message": "Giao dịch đã được xác nhận thành công"
}
```

### 2. Check Balance

**Endpoint**: `check_balance.php`

**Response**:
```json
{
  "success": true,
  "balance": 500000
}
```

### 3. Transaction Detail

**Endpoint**: `transaction_detail.php?id=123`

**Response**: HTML fragment hiển thị chi tiết giao dịch

### 4. Webhook

**Endpoint**: `webhook_payment.php`

**Method**: POST

**Headers**:
```
Content-Type: application/json
X-Webhook-Signature: <signature>
```

**Body**:
```json
{
  "type": "transaction.created",
  "data": {
    "transaction_id": "bank_tx_123",
    "amount": 100000,
    "description": "TS12345 Nap tien",
    "date": "2025-11-30 10:30:00"
  }
}
```

## Testing

### Test Cronjob Thủ Công

```bash
php cron_check_payment.php
```

### Test Auto Payment Check

```bash
php -r "require 'auto_payment_check.php'; \$processor = new AutoPaymentProcessor(\$conn); \$processor->process();"
```

### Test Single Transaction

```bash
php -r "require 'auto_payment_check.php'; \$processor = new AutoPaymentProcessor(\$conn); \$result = \$processor->checkSingleTransaction('TS12345'); print_r(\$result);"
```

## Hỗ Trợ Ngân Hàng

### Đã Implement (Template)

- ✅ VCB (Vietcombank)
- ✅ MB Bank
- ✅ ACB
- ✅ TPBank
- ✅ Techcombank
- ✅ VietinBank

**Lưu ý**: Do các API ngân hàng không công khai, bạn cần:
- Tự reverse engineer từ app mobile/web banking
- Hoặc sử dụng service provider (payment gateway) có sẵn
- Hoặc liên hệ ngân hàng để được cấp API chính thức

### Sử Dụng Service Provider (Khuyến Nghị)

Thay vì tự kết nối API ngân hàng (phức tạp và có thể vi phạm ToS), nên sử dụng:

- **Casso.vn** - Service tự động check giao dịch ngân hàng
- **PayOS** - Payment gateway Việt Nam
- **VNPay, MoMo, ZaloPay** - Cổng thanh toán chính thức

Để sử dụng, update `bank_api_helper.php`:

```php
// Cấu hình Casso
define('USE_COMMUNITY_API', true);
define('COMMUNITY_API_URL', 'https://oauth.casso.vn/v2/transactions');
define('COMMUNITY_API_KEY', 'your_api_key');
```

## Bảo Mật

### Quan Trọng

1. **Đổi secret keys** trong `payment_config.php`
2. **Không commit** file config lên git (thêm vào `.gitignore`)
3. **Bảo vệ webhook endpoint** bằng signature verification
4. **Sử dụng HTTPS** cho tất cả API endpoints
5. **Giới hạn rate limit** cho các API endpoints
6. **Log monitoring** để phát hiện bất thường

### .gitignore

```
payment_config.php
logs/*.log
```

## Troubleshooting

### Cronjob không chạy

```bash
# Check cronjob có đang chạy không
ps aux | grep cron_check_payment

# Check log cronjob
tail -f logs/cron.log

# Test chạy thủ công
php cron_check_payment.php
```

### Không kết nối được API ngân hàng

- Check credentials trong `payment_config.php`
- Check log: `logs/payment.log`
- Test login thủ công qua postman
- Check firewall/proxy có block không

### Giao dịch không tự động xác nhận

- Check cronjob có chạy không
- Check `PAYMENT_AUTO_CHECK_ENABLED = true`
- Check log để xem lỗi gì
- Check unique_code và amount có khớp không
- Check format nội dung chuyển khoản

### Lock file không tự xóa

```bash
# Xóa lock file thủ công
rm logs/payment_cron.lock
```

## Support

Nếu gặp vấn đề, check:

1. **Log files**: `logs/payment.log` và `logs/cron.log`
2. **Database**: Check bảng `transactions`
3. **Cronjob**: Check cronjob có chạy đúng không
4. **Config**: Check `payment_config.php`

## License

MIT License - Free to use and modify

---

**Tác giả**: Auto Payment System  
**Version**: 1.0.0  
**Ngày**: 2025-11-30
