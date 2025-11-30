# Hệ Thống Thanh Toán Tự Động - API Documentation

## 📋 Tổng Quan

Hệ thống thanh toán tự động cho phép tự động xác nhận và cộng tiền vào tài khoản khách hàng khi họ chuyển khoản, không cần admin xác nhận thủ công.

## 🚀 Tính Năng Chính

- ✅ **Thanh toán tự động**: Tự động xác nhận giao dịch khi nhận được thông tin từ ngân hàng
- ✅ **Webhook API**: Nhận thông báo realtime từ ngân hàng/cổng thanh toán
- ✅ **Cron Job**: Tự động kiểm tra giao dịch định kỳ
- ✅ **Hỗ trợ đa ngân hàng**: MB Bank, VCB, ACB, Techcombank, VietQR
- ✅ **Hỗ trợ cổng thanh toán**: VNPay, Momo
- ✅ **Log chi tiết**: Ghi log tất cả giao dịch để kiểm tra
- ✅ **Bảo mật**: Token authentication, IP whitelist
- ✅ **Transaction safety**: Sử dụng database transaction để đảm bảo tính toàn vẹn

## 📁 Cấu Trúc File

```
/workspace/
├── config_payment.php              # Cấu hình API thanh toán
├── payment_helper.php              # Helper xử lý logic thanh toán
├── api_payment_webhook.php         # API nhận webhook từ ngân hàng
├── api_check_bank_transactions.php # API kiểm tra giao dịch tự động (cron)
├── check_transaction_status.php    # API kiểm tra trạng thái giao dịch
├── check_balance.php              # API kiểm tra số dư
├── update_database_schema.php     # Script cập nhật database
├── setup_cron.sh                  # Script cài đặt cron job
├── test_webhook.php               # Script test webhook
└── logs/
    ├── payment.log                # Log thanh toán
    └── cron.log                   # Log cron job
```

## 🔧 Cài Đặt

### Bước 1: Cập nhật Database

Chạy script để cập nhật cấu trúc database:

```bash
php update_database_schema.php
```

Hoặc truy cập: `https://yourdomain.com/update_database_schema.php`

Script này sẽ:
- Thêm cột `bank_transaction_ref` vào bảng `transactions`
- Thêm cột `updated_at` vào bảng `transactions`
- Thêm index cho các cột để tăng tốc độ
- Tạo bảng `payment_logs` để lưu log chi tiết
- Tạo bảng `receiving_accounts` (nếu chưa có)
- Tạo thư mục `logs/` để lưu log file

### Bước 2: Cấu Hình

Mở file `config_payment.php` và cập nhật:

```php
// 1. Thay đổi API keys bảo mật
define('API_SECRET_KEY', 'your-secret-key-here');
define('WEBHOOK_TOKEN', 'your-webhook-token-here');

// 2. Cấu hình ngân hàng (nếu có API)
$bank_api_config = [
    'enabled' => true,
    'bank_type' => 'mbbank', // hoặc vcb, acb, techcombank
    'api_url' => 'https://api.bank.com',
    'username' => 'your_username',
    'password' => 'your_password',
    'account_number' => 'your_account_number',
];

// 3. Cấu hình VNPay (nếu dùng)
$vnpay_config = [
    'enabled' => true,
    'vnp_TmnCode' => 'YOUR_TMN_CODE',
    'vnp_HashSecret' => 'YOUR_HASH_SECRET',
    'vnp_Url' => 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
];

// 4. Cấu hình Momo (nếu dùng)
$momo_config = [
    'enabled' => true,
    'partner_code' => 'YOUR_PARTNER_CODE',
    'access_key' => 'YOUR_ACCESS_KEY',
    'secret_key' => 'YOUR_SECRET_KEY',
];

// 5. Whitelist IP (cho webhook)
$allowed_webhook_ips = [
    '127.0.0.1',
    'IP_CUA_NGAN_HANG', // Thêm IP của ngân hàng vào đây
];
```

### Bước 3: Cài Đặt Cron Job

#### Cách 1: Dùng script tự động (Linux/Mac)

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

#### Cách 2: Cài đặt thủ công

Mở crontab:
```bash
crontab -e
```

Thêm dòng sau (chạy mỗi phút):
```bash
* * * * * cd /path/to/your/project && php api_check_bank_transactions.php >> logs/cron.log 2>&1
```

#### Cách 3: Dùng HTTP cron (nếu không có SSH)

Tạo cron job gọi URL:
```
https://yourdomain.com/api_check_bank_transactions.php?secret=YOUR_SECRET_KEY
```

### Bước 4: Cấu Hình Webhook

#### Với ngân hàng có API:

Đăng ký webhook URL với ngân hàng:
```
https://yourdomain.com/api_payment_webhook.php
```

#### Với VNPay:

1. Đăng ký Return URL trong merchant portal:
   ```
   https://yourdomain.com/api_payment_webhook.php?type=vnpay
   ```

#### Với Momo:

1. Đăng ký IPN URL trong merchant portal:
   ```
   https://yourdomain.com/api_payment_webhook.php?type=momo
   ```

## 📖 Cách Sử Dụng

### Flow Thanh Toán

1. **Khách hàng tạo lệnh nạp tiền** (trên `deposit.php`):
   - Nhập số tiền muốn nạp
   - Hệ thống tạo giao dịch với status `pending` và mã unique code (ví dụ: `TS00001`)
   - Hiển thị thông tin chuyển khoản cho khách

2. **Khách hàng chuyển khoản**:
   - Chuyển khoản đến tài khoản ngân hàng
   - Ghi nội dung: mã unique code (ví dụ: `TS00001`)

3. **Hệ thống xác nhận tự động** (2 cách):

   **Cách 1: Webhook (Realtime)**
   - Ngân hàng/cổng thanh toán gửi thông báo đến API webhook
   - Hệ thống nhận và xử lý ngay lập tức
   - Cập nhật trạng thái giao dịch → `success`
   - Cộng tiền vào tài khoản khách hàng

   **Cách 2: Cron Job (Định kỳ)**
   - Cron job chạy định kỳ (mỗi phút)
   - Lấy danh sách giao dịch `pending`
   - Gọi API ngân hàng kiểm tra từng giao dịch
   - Nếu tìm thấy → xử lý thanh toán tự động

4. **Khách hàng nhận tiền**:
   - Số dư được cập nhật tự động
   - Trang deposit.php tự động reload khi phát hiện số dư thay đổi

### API Endpoints

#### 1. Webhook API

**URL**: `POST /api_payment_webhook.php`

**Headers**:
```
Content-Type: application/json
X-Webhook-Token: YOUR_WEBHOOK_TOKEN
```

**Request Body** (Chuyển khoản ngân hàng):
```json
{
  "type": "bank_transfer",
  "token": "YOUR_WEBHOOK_TOKEN",
  "description": "TS00001",
  "amount": 100000,
  "transaction_id": "BANK_REF_123",
  "bank_name": "MB Bank",
  "account_number": "0123456789",
  "transaction_date": "2025-11-30 10:30:00"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Payment processed successfully",
  "data": {
    "success": true,
    "transaction_id": 123,
    "user_id": 456,
    "amount": 100000
  }
}
```

#### 2. Cron Job API

**URL**: `GET /api_check_bank_transactions.php?secret=YOUR_SECRET_KEY`

**Response**:
```json
{
  "success": true,
  "message": "Check completed",
  "pending_count": 5,
  "processed": 2,
  "success": 2,
  "cancelled": 1
}
```

#### 3. Check Transaction Status

**URL**: `GET /check_transaction_status.php?code=TS00001`

**Response**:
```json
{
  "success": true,
  "transaction_id": 123,
  "amount": "100,000",
  "status": "success",
  "transaction_date": "30/11/2025 10:30:00",
  "updated_at": "30/11/2025 10:31:00",
  "bank_ref": "BANK_REF_123"
}
```

#### 4. Check Balance

**URL**: `GET /check_balance.php`

**Response**:
```json
{
  "success": true,
  "balance": 500000,
  "balance_formatted": "500,000"
}
```

## 🧪 Test

### Test Webhook

1. Chỉnh sửa file `test_webhook.php`:
   ```php
   $webhook_url = 'http://your-domain.com/api_payment_webhook.php';
   $test_data['description'] = 'TS00001'; // Mã giao dịch có trong DB
   $test_data['amount'] = 100000; // Số tiền khớp với giao dịch
   ```

2. Chạy test:
   ```bash
   php test_webhook.php
   ```

3. Kiểm tra kết quả:
   - Xem output của script
   - Kiểm tra file `logs/payment.log`
   - Kiểm tra database: bảng `transactions` và `payment_logs`
   - Kiểm tra số dư user đã tăng

### Test Cron Job

```bash
php api_check_bank_transactions.php
```

Hoặc:
```bash
curl "https://yourdomain.com/api_check_bank_transactions.php?secret=YOUR_SECRET_KEY"
```

## 🔐 Bảo Mật

1. **Thay đổi tất cả secret keys** trong `config_payment.php`
2. **Whitelist IP** cho webhook (nếu có IP cố định từ ngân hàng)
3. **Bảo vệ thư mục logs**:
   - File `.htaccess` đã được tạo tự động
   - Hoặc cấu hình nginx/apache để deny access
4. **HTTPS**: Luôn dùng HTTPS cho production
5. **Xóa file test**: Xóa `test_webhook.php` sau khi test xong

## 📊 Database Schema

### Bảng `transactions`

```sql
ALTER TABLE transactions 
ADD COLUMN bank_transaction_ref VARCHAR(100) DEFAULT NULL AFTER unique_code,
ADD COLUMN updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
ADD INDEX idx_unique_code (unique_code),
ADD INDEX idx_status (status);
```

### Bảng `payment_logs`

```sql
CREATE TABLE payment_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  transaction_id INT,
  user_id INT,
  unique_code VARCHAR(50),
  amount DECIMAL(15,2),
  bank_transaction_ref VARCHAR(100),
  status VARCHAR(50),
  extra_data TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_transaction (transaction_id),
  INDEX idx_user (user_id),
  INDEX idx_unique_code (unique_code)
);
```

## 🐛 Troubleshooting

### Webhook không hoạt động

1. Kiểm tra log: `logs/payment.log`
2. Kiểm tra webhook token có đúng không
3. Kiểm tra IP có trong whitelist không
4. Test bằng `test_webhook.php`

### Cron job không chạy

1. Kiểm tra cron đã được cài đặt: `crontab -l`
2. Kiểm tra log: `logs/cron.log`
3. Kiểm tra quyền thực thi file PHP
4. Test chạy thủ công: `php api_check_bank_transactions.php`

### Giao dịch không được xử lý

1. Kiểm tra mã unique code có đúng không
2. Kiểm tra số tiền có khớp không (chấp nhận sai số 1 VND)
3. Kiểm tra status giao dịch có phải `pending` không
4. Xem log chi tiết trong `payment_logs`

### Lỗi database

1. Chạy lại `update_database_schema.php`
2. Kiểm tra quyền user database
3. Kiểm tra kết nối database trong `db.php`

## 📝 Log Files

### payment.log

Ghi log tất cả hoạt động thanh toán:
```
[2025-11-30 10:30:00] Bắt đầu xử lý thanh toán tự động cho mã: TS00001, số tiền: 100000
[2025-11-30 10:30:01] Xử lý thanh toán thành công cho mã: TS00001
```

### cron.log

Ghi log của cron job:
```
{"success":true,"message":"Check completed","pending_count":5,"processed":2,"success":2}
```

## 🔄 Flow Chart

```
┌─────────────────┐
│ Khách tạo lệnh  │
│   nạp tiền      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Tạo giao dịch   │
│ status: pending │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Khách chuyển    │
│   khoản         │
└────────┬────────┘
         │
         ├─────────────────────┐
         │                     │
         v                     v
┌──────────────────┐  ┌──────────────────┐
│ Webhook nhận     │  │ Cron job kiểm    │
│ thông báo        │  │ tra định kỳ      │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    v
         ┌─────────────────────┐
         │ payment_helper      │
         │ processAutoPayment  │
         └──────────┬──────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         v                     v
┌──────────────────┐  ┌──────────────────┐
│ Cập nhật status  │  │ Cộng tiền vào    │
│ → success        │  │ balance          │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    v
         ┌─────────────────────┐
         │ Ghi log & thông báo │
         └─────────────────────┘
```

## 🤝 Tích Hợp Với Ngân Hàng

### MB Bank

Liên hệ MB Bank để:
1. Đăng ký API Business Banking
2. Lấy API credentials (username, password, API key)
3. Đăng ký webhook URL
4. Lấy IP của hệ thống MB Bank để whitelist

### VCB (Vietcombank)

Tương tự MB Bank, liên hệ VCB để đăng ký API

### VNPay

1. Đăng ký merchant tại: https://vnpay.vn
2. Lấy `vnp_TmnCode` và `vnp_HashSecret`
3. Cấu hình Return URL và IPN URL

### Momo

1. Đăng ký merchant tại: https://business.momo.vn
2. Lấy `partner_code`, `access_key`, `secret_key`
3. Cấu hình IPN URL

### VietQR

1. Đăng ký tại: https://vietqr.io
2. Lấy API key
3. Sử dụng API để check giao dịch

## 📞 Hỗ Trợ

Nếu gặp vấn đề:

1. Kiểm tra log files trong thư mục `logs/`
2. Chạy test webhook: `php test_webhook.php`
3. Kiểm tra database: bảng `transactions` và `payment_logs`
4. Xem documentation của từng ngân hàng/cổng thanh toán

## 📄 License

Copyright © 2025 - VPN Việt Nam

---

**Lưu ý quan trọng**:
- Backup database trước khi cài đặt
- Test kỹ trên môi trường staging trước khi deploy production
- Thay đổi tất cả secret keys và tokens
- Xóa các file test sau khi hoàn thành
