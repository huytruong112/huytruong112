# 🚀 HƯỚNG DẪN CÀI ĐẶT NHANH - THANH TOÁN TỰ ĐỘNG

## ⚡ Cài Đặt 5 Phút

### Bước 1: Upload Files (1 phút)

Upload tất cả các file vào thư mục website của bạn:

```
✓ config_payment.php
✓ payment_helper.php
✓ api_payment_webhook.php
✓ api_check_bank_transactions.php
✓ check_transaction_status.php
✓ check_balance.php
✓ transaction_detail.php
✓ update_database_schema.php
✓ test_webhook.php
```

### Bước 2: Cập Nhật Database (30 giây)

Truy cập: `https://yourdomain.com/update_database_schema.php`

Hoặc chạy: `php update_database_schema.php`

✅ Xong! Database đã được cập nhật.

### Bước 3: Cấu Hình (2 phút)

Mở file `config_payment.php` và thay đổi:

```php
// QUAN TRỌNG: Thay đổi các key này!
define('API_SECRET_KEY', 'abc123xyz456'); // Đổi thành key bảo mật của bạn
define('WEBHOOK_TOKEN', 'webhook789token'); // Đổi thành token của bạn

// Nếu có API ngân hàng (tùy chọn):
$bank_api_config = [
    'enabled' => true,
    'bank_type' => 'mbbank', // hoặc vcb, acb, techcombank
    'api_url' => 'https://api.yourbank.com',
    'username' => 'your_username',
    'password' => 'your_password',
    'account_number' => '0123456789',
];
```

### Bước 4: Cài Cron Job (1 phút)

#### Linux/Mac:
```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

#### Windows hoặc Shared Hosting:

Tạo cron job chạy URL sau mỗi phút:
```
https://yourdomain.com/api_check_bank_transactions.php?secret=YOUR_SECRET_KEY
```

### Bước 5: Test (30 giây)

1. Mở file `test_webhook.php`
2. Sửa dòng:
   ```php
   $webhook_url = 'http://your-domain.com/api_payment_webhook.php';
   $test_data['description'] = 'TS00001'; // Mã giao dịch có trong DB
   ```
3. Chạy: `php test_webhook.php`
4. Xem kết quả ✅

---

## 🎯 XONG! Hệ thống đã sẵn sàng!

## 📖 Cách Hoạt Động

1. **Khách hàng nạp tiền** → Hệ thống tạo mã (ví dụ: TS00001)
2. **Khách chuyển khoản** với nội dung: TS00001
3. **Hệ thống tự động**:
   - Nhận webhook từ ngân hàng (nếu có)
   - Hoặc cron job kiểm tra định kỳ
   - Xác nhận và cộng tiền tự động ✅

## 🔧 Cấu Hình Webhook (Nếu Có)

### Với ngân hàng:
Đăng ký webhook URL:
```
https://yourdomain.com/api_payment_webhook.php
```

### Với VNPay:
Return URL:
```
https://yourdomain.com/api_payment_webhook.php?type=vnpay
```

### Với Momo:
IPN URL:
```
https://yourdomain.com/api_payment_webhook.php?type=momo
```

## 📁 File Quan Trọng

| File | Mục đích |
|------|----------|
| `config_payment.php` | Cấu hình API, keys, tokens |
| `payment_helper.php` | Xử lý logic thanh toán |
| `api_payment_webhook.php` | Nhận webhook từ ngân hàng |
| `api_check_bank_transactions.php` | Cron job kiểm tra tự động |

## 🐛 Khắc Phục Lỗi Nhanh

### Webhook không hoạt động?
1. Kiểm tra `logs/payment.log`
2. Test: `php test_webhook.php`
3. Kiểm tra WEBHOOK_TOKEN có đúng không

### Cron job không chạy?
1. Kiểm tra: `crontab -l`
2. Xem log: `logs/cron.log`
3. Test: `php api_check_bank_transactions.php`

### Giao dịch không tự động?
1. Kiểm tra mã unique_code có đúng không
2. Kiểm tra số tiền có khớp không
3. Xem log: `logs/payment.log`

## 📞 Liên Hệ & Hỗ Trợ

- 📧 Email: admin@yourdomain.com
- 📱 Hotline: 0812.363.898
- 📖 Docs đầy đủ: `README_PAYMENT_API.md`

## ⚠️ Lưu Ý Quan Trọng

1. ✅ **LUÔN backup database trước khi cài đặt**
2. ✅ **Thay đổi tất cả secret keys và tokens**
3. ✅ **Test trên staging trước khi deploy production**
4. ✅ **Xóa file test_webhook.php sau khi test xong**
5. ✅ **Sử dụng HTTPS cho production**

## 🎉 Hoàn Thành!

Hệ thống thanh toán tự động đã sẵn sàng hoạt động!

Xem hướng dẫn chi tiết trong file `README_PAYMENT_API.md`

---

**Version**: 1.0  
**Last Update**: 30/11/2025  
**Copyright**: VPN Việt Nam
