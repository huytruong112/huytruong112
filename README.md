# 💳 HỆ THỐNG THANH TOÁN TỰ ĐỘNG - VPN VIỆT NAM

Hệ thống thanh toán tự động cho phép khách hàng nạp tiền và được cộng số dư ngay lập tức khi chuyển khoản ngân hàng, không cần admin xác nhận thủ công.

## 🚀 Tính năng chính

- ✅ **Thanh toán tự động 100%** - Không cần admin xác nhận
- ✅ **Realtime** - Cộng tiền trong vòng 2-5 giây sau khi chuyển khoản
- ✅ **Đa dạng nguồn** - Hỗ trợ Casso.vn, Payos.vn, API ngân hàng
- ✅ **Bảo mật cao** - IP whitelist, secret key, secure token
- ✅ **Log chi tiết** - Lưu vết mọi giao dịch
- ✅ **Admin dashboard** - Xem thống kê và quản lý thanh toán
- ✅ **Tự động hủy** - Giao dịch quá hạn 24h tự động cancel

## 📁 Cấu trúc dự án

```
/workspace/
├── 📄 payment_config.php           # Cấu hình API và settings
├── 📄 payment_processor.php        # Class xử lý logic thanh toán
├── 📄 payment_webhook.php          # API endpoint nhận webhook ⭐
├── 📄 payment_logs.php            # Trang admin xem logs
├── 📄 payment_schema.sql          # SQL cập nhật database
├── 📄 db.php                      # Kết nối database
├── 📄 check_balance.php           # API kiểm tra số dư
├── 📄 check_transaction_status.php # API kiểm tra trạng thái GD
├── 📄 transaction_detail.php       # Xem chi tiết giao dịch
├── 📄 test_webhook.php            # File test webhook
├── 📄 HUONG_DAN_THANH_TOAN_TU_DONG.md  # Hướng dẫn chi tiết
└── 📁 logs/                       # Thư mục chứa log files
    └── payment_webhook.log
```

## 🔧 Cài đặt nhanh

### 1. Import database

```bash
mysql -u root -p vpn_vietnam < payment_schema.sql
```

### 2. Cấu hình API

Mở `payment_config.php` và chỉnh sửa:

```php
define('PAYMENT_ENABLED', true);
define('WEBHOOK_SECRET', 'your-secret-key-here');
define('CASSO_API_KEY', 'YOUR_CASSO_API_KEY');
define('CASSO_SECURE_TOKEN', 'YOUR_CASSO_SECURE_TOKEN');
```

### 3. Tạo thư mục logs

```bash
mkdir logs
chmod 755 logs
```

### 4. Đăng ký webhook tại Casso.vn

URL webhook: `https://yourdomain.com/payment_webhook.php?source=casso`

## 🧪 Test hệ thống

```bash
# Test webhook hoạt động
curl "https://yourdomain.com/payment_webhook.php?test=1"

# Test giao dịch
php test_webhook.php
```

## 📊 Xem logs

Truy cập: `https://yourdomain.com/payment_logs.php`

- Yêu cầu đăng nhập với tài khoản admin (role = 'admin')
- Xem tất cả log thanh toán
- Thống kê theo ngày, tháng
- Lọc theo trạng thái, nguồn

## 🔄 Luồng hoạt động

```
1. User tạo yêu cầu nạp tiền → Nhận mã TSxxxxx
2. User chuyển khoản với nội dung TSxxxxx
3. Ngân hàng → Casso.vn → Webhook của bạn
4. Webhook tự động:
   - Tìm giao dịch theo mã TSxxxxx
   - Kiểm tra số tiền
   - Cộng tiền vào tài khoản
   - Lưu log
5. User thấy số dư được cập nhật ngay lập tức
```

## 🔐 Bảo mật

### IP Whitelist
Chỉ cho phép IP của Casso/Payos gọi webhook

### Secret Key
Xác thực mọi request đến webhook

### Secure Token
Casso gửi token bảo mật trong mỗi request

### Anti-duplicate
Tự động phát hiện và bỏ qua webhook trùng lặp

## 📚 Tài liệu

- **Hướng dẫn chi tiết:** [HUONG_DAN_THANH_TOAN_TU_DONG.md](HUONG_DAN_THANH_TOAN_TU_DONG.md)
- **API Documentation:** Xem comment trong mỗi file PHP
- **Database Schema:** [payment_schema.sql](payment_schema.sql)

## ⚙️ Yêu cầu hệ thống

- PHP 7.4+
- MySQL 5.7+ / MariaDB 10.3+
- Extension: mysqli, curl, json
- Apache/Nginx với mod_rewrite
- HTTPS (bắt buộc cho webhook)

## 🌐 Dịch vụ hỗ trợ

### Casso.vn (Khuyến nghị ⭐)
- Hỗ trợ 30+ ngân hàng VN
- Webhook realtime < 5s
- Giá từ 99k/tháng
- Đăng ký: https://casso.vn/

### Payos.vn
- QR code thanh toán
- Nhiều phương thức
- Đăng ký: https://payos.vn/

## 🐛 Xử lý lỗi phổ biến

### "Transaction not found"
→ User ghi sai mã hoặc mã không tồn tại

### "Amount mismatch"
→ Số tiền chuyển khác số tiền yêu cầu

### "Access denied"
→ IP không trong whitelist

### "Already processed"
→ Giao dịch đã xử lý (bảo vệ duplicate)

Chi tiết: Xem [HUONG_DAN_THANH_TOAN_TU_DONG.md](HUONG_DAN_THANH_TOAN_TU_DONG.md)

## 📈 Monitoring

```bash
# Xem log realtime
tail -f logs/payment_webhook.log

# Xem thống kê
mysql> SELECT * FROM payment_statistics;

# Kiểm tra event scheduler
mysql> SHOW VARIABLES LIKE 'event_scheduler';
```

## 🔄 Cập nhật

```bash
# Backup trước khi cập nhật
mysqldump -u root -p vpn_vietnam payment_logs > backup.sql

# Pull code mới
git pull origin main

# Chạy migration (nếu có)
mysql -u root -p vpn_vietnam < migrations/xxx.sql
```

## 📞 Liên hệ & Hỗ trợ

- 📧 Email: admin@vpnvietnam.com
- 📱 Hotline: 0812.363.898
- 💬 Telegram: @vpnvietnam_support

## 📝 License

© 2025 VPN Việt Nam. All rights reserved.

---

**Made with ❤️ by VPN Việt Nam Team**
