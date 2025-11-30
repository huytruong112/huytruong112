# 🚀 Hệ Thống API Thanh Toán Tự Động

Hệ thống thanh toán tự động cho phép khách hàng nạp tiền qua chuyển khoản ngân hàng và tự động được xác nhận mà không cần xử lý thủ công.

## ✨ Tính Năng Chính

- ✅ **Tự động kiểm tra giao dịch** - Kết nối API ngân hàng/Casso để lấy lịch sử giao dịch
- ✅ **So khớp thông minh** - Tự động so khớp mã giao dịch và số tiền
- ✅ **Cập nhật realtime** - Tự động cộng tiền vào tài khoản ngay khi xác nhận
- ✅ **Webhook hỗ trợ** - Nhận callback realtime từ ngân hàng (nếu có)
- ✅ **Cronjob tự động** - Kiểm tra định kỳ mỗi phút
- ✅ **Hủy giao dịch tự động** - Tự động hủy giao dịch pending quá 24h
- ✅ **Logging đầy đủ** - Ghi log chi tiết mọi hoạt động
- ✅ **Hỗ trợ đa ngân hàng** - VCB, MB Bank, ACB, TPBank, Techcombank, VietinBank
- ✅ **Bảo mật cao** - Signature verification, IP whitelist, HTTPS
- ✅ **Dễ tích hợp** - API đơn giản, document chi tiết

## 📁 Cấu Trúc File

```
/workspace/
├── payment_config.php              # ⚙️ Cấu hình chính
├── bank_api_helper.php             # 🏦 Helper kết nối API ngân hàng
├── bank_api_casso.php              # 💳 Tích hợp Casso.vn (khuyến nghị)
├── auto_payment_check.php          # 🔄 Script xử lý thanh toán tự động
├── auto_payment_check_casso.php    # 🔄 Script xử lý với Casso
├── webhook_payment.php             # 🔔 Webhook cho ngân hàng
├── webhook_payment_casso.php       # 🔔 Webhook cho Casso
├── cron_check_payment.php          # ⏰ Cronjob định kỳ
├── check_transaction_status.php    # 📊 API check trạng thái giao dịch
├── check_balance.php               # 💰 API check số dư
├── transaction_detail.php          # 📝 Hiển thị chi tiết giao dịch
├── setup_payment.php               # 🛠️ Script cài đặt tự động
├── test_payment_system.php         # 🧪 Test hệ thống
├── db_schema.sql                   # 🗄️ Database schema
├── README.md                       # 📖 File này
├── README_PAYMENT_API.md           # 📚 Document chi tiết
├── HUONG_DAN_CAI_DAT.md           # 🇻🇳 Hướng dẫn tiếng Việt
├── .gitignore                      # 🚫 Git ignore
└── logs/                           # 📋 Thư mục log
    ├── payment.log
    └── cron.log
```

## 🚀 Cài Đặt Nhanh (5 phút)

### Bước 1: Clone/Upload Files

```bash
# Clone repository (hoặc upload files lên server)
cd /path/to/your/project
```

### Bước 2: Chạy Setup

```bash
php setup_payment.php
```

Script này sẽ tự động:
- Kiểm tra PHP version & extensions
- Tạo thư mục logs
- Phân quyền files
- Kiểm tra database
- Tạo crontab example

### Bước 3: Cấu Hình

Mở file `payment_config.php` và cấu hình:

```php
// Sử dụng Casso (khuyến nghị)
define('USE_COMMUNITY_API', true);
define('COMMUNITY_API_KEY', 'your-casso-api-key');

// Hoặc kết nối trực tiếp ngân hàng (không khuyến nghị)
define('BANK_API_TYPE', 'vcb');
define('VCB_USERNAME', 'your_username');
define('VCB_PASSWORD', 'your_password');
```

### Bước 4: Cài Đặt Database

```bash
mysql -u username -p database_name < db_schema.sql
```

### Bước 5: Cài Đặt Cronjob

```bash
crontab -e
```

Thêm dòng:

```bash
*/1 * * * * /usr/bin/php /path/to/cron_check_payment_casso.php >> /path/to/logs/cron.log 2>&1
```

### Bước 6: Test

```bash
php test_payment_system.php
```

Nếu tất cả test PASS → Hệ thống sẵn sàng! 🎉

## 📖 Documents

- **[README_PAYMENT_API.md](README_PAYMENT_API.md)** - Document chi tiết (English)
- **[HUONG_DAN_CAI_DAT.md](HUONG_DAN_CAI_DAT.md)** - Hướng dẫn cài đặt (Tiếng Việt)

## 🔧 Cách Sử Dụng

### 1. Khách Hàng Nạp Tiền

1. User truy cập trang nạp tiền
2. Nhập số tiền muốn nạp (VD: 100,000 VND)
3. Hệ thống tạo mã giao dịch unique (VD: **TS12345**)
4. Hiển thị thông tin chuyển khoản

### 2. User Chuyển Khoản

User chuyển khoản với:
- **Số tiền**: 100,000 VND
- **Nội dung**: **TS12345** (phải chính xác)

### 3. Hệ Thống Tự Động Xác Nhận

- Cronjob chạy mỗi phút (hoặc webhook realtime)
- Lấy danh sách giao dịch từ ngân hàng
- So khớp mã TS12345 và số tiền
- Nếu khớp:
  - ✅ Cập nhật transaction: `status = 'success'`
  - ✅ Cộng tiền vào user: `balance += 100,000`
  - ✅ Ghi log

### 4. User Nhận Thông Báo

- Frontend tự động refresh số dư mỗi 10s
- Hiển thị "Đã thanh toán"
- User có thể sử dụng số dư để mua dịch vụ

## 🏦 Hỗ Trợ Ngân Hàng

### ✅ Qua Casso.vn (Khuyến Nghị)

- **Vietcombank (VCB)**
- **MB Bank**
- **ACB**
- **Techcombank**
- **VietinBank**
- **TPBank**
- **Sacombank**
- **VPBank**
- **Và hơn 20+ ngân hàng khác**

**Đăng ký**: https://casso.vn  
**Giá**: Từ 299,000 VND/tháng (trial 7 ngày miễn phí)

### ⚠️ Kết Nối Trực Tiếp (Không Khuyến Nghị)

- Phức tạp, cần reverse engineer
- Có thể vi phạm ToS ngân hàng
- API thay đổi bất kỳ lúc nào
- Rủi ro bảo mật cao

## 🔔 Webhook

### Cấu Hình Webhook Casso

1. Vào: https://casso.vn/dashboard
2. Chọn "Webhook"
3. Nhập URL: `https://yourdomain.com/webhook_payment_casso.php`
4. Chọn "Tiền vào"
5. Save

### Test Webhook

```bash
curl -X POST https://yourdomain.com/webhook_payment_casso.php \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "id": "123",
      "amount": 100000,
      "description": "TS12345 Nap tien",
      "when": 1640995200000
    }
  }'
```

## 🧪 Testing

### Test Toàn Bộ Hệ Thống

```bash
php test_payment_system.php
```

### Test Cronjob

```bash
php cron_check_payment_casso.php
```

### Test API

```bash
# Check balance
curl https://yourdomain.com/check_balance.php

# Check transaction status
curl https://yourdomain.com/check_transaction_status.php?code=TS12345
```

### Xem Log

```bash
# Log payment
tail -f logs/payment.log

# Log cronjob
tail -f logs/cron.log

# Theo dõi realtime
tail -f logs/payment.log logs/cron.log
```

## 🔒 Bảo Mật

### Checklist Bảo Mật

- [ ] Đổi `WEBHOOK_SECRET` trong config
- [ ] Đổi `PAYMENT_API_SECRET` trong config
- [ ] Không commit `payment_config.php` lên git
- [ ] Sử dụng HTTPS cho tất cả endpoints
- [ ] Whitelist IP cho webhook
- [ ] Giới hạn rate limit
- [ ] Backup database định kỳ
- [ ] Monitor logs để phát hiện bất thường

### Whitelist Casso IPs

**Nginx**:
```nginx
location /webhook_payment_casso.php {
    allow 172.105.162.113;
    allow 139.162.29.153;
    deny all;
}
```

**Apache**:
```apache
<Location /webhook_payment_casso.php>
    Require ip 172.105.162.113
    Require ip 139.162.29.153
</Location>
```

## 📊 API Endpoints

### 1. Check Transaction Status

**GET** `/check_transaction_status.php?code=TS12345`

**Response**:
```json
{
  "success": true,
  "status": "success",
  "transaction_id": 123,
  "amount": 100000,
  "date": "2025-11-30 10:30:00"
}
```

### 2. Check Balance

**GET** `/check_balance.php`

**Response**:
```json
{
  "success": true,
  "balance": 500000
}
```

### 3. Transaction Detail

**GET** `/transaction_detail.php?id=123`

**Response**: HTML fragment

## 🛠️ Troubleshooting

### Cronjob không chạy

```bash
# Check crontab
crontab -l

# Check log
tail -f logs/cron.log

# Test thủ công
php cron_check_payment_casso.php
```

### Không kết nối được Casso

```bash
# Test API key
curl -H "Authorization: Apikey YOUR_API_KEY" \
  "https://oauth.casso.vn/v2/userInfo"
```

### Giao dịch không tự động xác nhận

1. Check cronjob có chạy: `tail -f logs/cron.log`
2. Check log payment: `tail -f logs/payment.log`
3. Check nội dung CK: Phải đúng mã (VD: TS12345)
4. Check số tiền: Phải khớp chính xác
5. Check status trong DB: `SELECT * FROM transactions WHERE unique_code='TS12345'`

## 💡 Best Practices

1. **Sử dụng Casso** thay vì kết nối trực tiếp API ngân hàng
2. **Bật webhook** để có thông báo realtime
3. **Monitor logs** thường xuyên
4. **Backup database** hàng ngày
5. **Test trên staging** trước khi deploy production
6. **Sử dụng HTTPS** bắt buộc
7. **Whitelist IP** cho webhook
8. **Đổi secret keys** định kỳ

## 📞 Support

- **Email**: support@yourdomain.com
- **Hotline**: 0812.363.898
- **Casso Support**: support@casso.vn
- **GitHub Issues**: [Link to your repo]

## 📝 License

MIT License - Free to use and modify

## 🙏 Credits

- **Casso.vn** - Service tự động check giao dịch ngân hàng
- **Bootstrap** - UI Framework
- **Font Awesome** - Icons

## 📈 Roadmap

- [ ] Hỗ trợ QR Code thanh toán
- [ ] Tích hợp VNPay, MoMo, ZaloPay
- [ ] Push notification cho mobile app
- [ ] Dashboard thống kê giao dịch
- [ ] Export báo cáo Excel
- [ ] Multi-currency support
- [ ] Refund automation

## 🎉 Changelog

### Version 1.0.0 (2025-11-30)

- ✅ Initial release
- ✅ Tích hợp Casso.vn
- ✅ Webhook support
- ✅ Cronjob automation
- ✅ Full logging
- ✅ Auto cancel expired transactions
- ✅ Complete documentation

---

**Made with ❤️ for Vietnamese VPN Service**

**Chúc bạn thành công!** 🚀
