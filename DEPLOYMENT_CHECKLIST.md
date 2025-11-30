# ✅ CHECKLIST TRIỂN KHAI BẢO MẬT

## 📋 DANH SÁCH KIỂM TRA TRƯỚC KHI DEPLOY

### 🔰 Chuẩn Bị

- [ ] **Backup dữ liệu**
  - [ ] Backup database hiện tại
  - [ ] Backup file `pay.php` cũ
  - [ ] Backup toàn bộ thư mục website
  - [ ] Lưu backup ở vị trí an toàn

- [ ] **Môi trường**
  - [ ] PHP version >= 7.4
  - [ ] MySQL/MariaDB đang chạy
  - [ ] SSL/HTTPS đã được cài đặt
  - [ ] Có quyền write vào thư mục web

- [ ] **Review code**
  - [ ] Đã đọc `SECURITY_IMPROVEMENTS.md`
  - [ ] Đã đọc `README_NANG_CAP_BAO_MAT.md`
  - [ ] Hiểu rõ các thay đổi
  - [ ] Đã mở `demo_security_comparison.html` để xem demo

---

### 📥 Tải Files

- [ ] **Download files mới từ repo:**
  - [ ] `pay.php` (version mới)
  - [ ] `qr_proxy.php` (file mới)
  - [ ] `SECURITY_IMPROVEMENTS.md` (optional - tài liệu)
  - [ ] `README_NANG_CAP_BAO_MAT.md` (optional - hướng dẫn)

---

### 🔧 Cấu Hình

- [ ] **Cấu hình APP_SECRET**
  - [ ] Mở file `config.php`
  - [ ] Thêm dòng: `define('APP_SECRET', 'your-secret-key-here');`
  - [ ] Secret key >= 32 ký tự
  - [ ] Secret key phức tạp (chữ, số, ký tự đặc biệt)
  - [ ] KHÔNG dùng secret mặc định `change-this-secret-32bytes-min`
  - [ ] Lưu file `config.php`

**Ví dụ APP_SECRET mạnh:**
```php
define('APP_SECRET', 'xK9#mQ2$vL8@nR5!wB3^yF7&zD1*pE6+tJ4%hG0');
```

**Tạo secret key ngẫu nhiên (Linux/Mac):**
```bash
openssl rand -base64 48
```

---

### 📤 Upload Files

- [ ] **Kết nối FTP/SFTP/cPanel**
  - [ ] Đăng nhập thành công
  - [ ] Navigate tới thư mục web root
  
- [ ] **Upload file `qr_proxy.php`**
  - [ ] Upload lên thư mục gốc (cùng cấp với `pay.php`)
  - [ ] Verify file tồn tại: `https://yourdomain.com/qr_proxy.php` (sẽ trả về lỗi - đúng)

- [ ] **Thay thế file `pay.php`**
  - [ ] Rename `pay.php` cũ thành `pay.php.backup`
  - [ ] Upload `pay.php` mới
  - [ ] Verify file size > 0 bytes
  
- [ ] **Set permissions (nếu cần)**
  ```bash
  chmod 644 pay.php
  chmod 644 qr_proxy.php
  ```

---

### 🧪 Test Trên Staging (Nên Có)

- [ ] **Test trên môi trường staging trước**
  - [ ] Deploy lên staging server
  - [ ] Chạy test cases (xem bên dưới)
  - [ ] Fix bugs nếu có
  - [ ] Confirm staging chạy OK

---

### ✅ Test Chức Năng

#### Test 1: Trang thanh toán load bình thường
- [ ] Truy cập: `pay.php?code=[MÃ_GIAO_DỊCH_HỢP_LỆ]`
- [ ] Trang load không lỗi 500
- [ ] Thông tin khách hàng hiển thị đúng
- [ ] Số tiền hiển thị đúng

#### Test 2: Thông tin ngân hàng hiển thị
- [ ] Tên ngân hàng hiển thị rõ ràng (không phải `***`)
- [ ] Số tài khoản hiển thị rõ ràng
- [ ] Tên chủ tài khoản hiển thị rõ ràng
- [ ] Chi nhánh hiển thị (nếu có)

#### Test 3: QR Code hiển thị
- [ ] QR Code image xuất hiện
- [ ] QR Code rõ nét, không bị lỗi
- [ ] Click vào QR Code không bị lỗi 403/404
- [ ] Scan QR Code bằng app ngân hàng → Thông tin đúng

#### Test 4: View Source Code (QUAN TRỌNG)
- [ ] Right-click → View Page Source
- [ ] Tìm kiếm số tài khoản → **KHÔNG TÌM THẤY**
- [ ] Tìm kiếm tên chủ TK → **KHÔNG TÌM THẤY**
- [ ] QR URL là `qr_proxy.php?code=...&sig=...` ✅
- [ ] Thông tin ngân hàng trong HTML là `***` ✅
- [ ] Có đoạn mã hóa dạng: `decodeBankInfo('f4e9a2...')` ✅

#### Test 5: JavaScript Console
- [ ] Mở F12 → Console tab
- [ ] Không có lỗi đỏ (errors)
- [ ] Console log không in ra thông tin ngân hàng
- [ ] Thử chạy: `decodeBankInfo('f4e9a2...')` → Không decode được vì thiếu context

#### Test 6: Email gửi thành công
- [ ] Tạo giao dịch mới
- [ ] Email hướng dẫn thanh toán được gửi
- [ ] Email có đầy đủ thông tin (email vẫn chứa plaintext - OK)
- [ ] Link trong email hoạt động

#### Test 7: Button "Gửi lại email"
- [ ] Click button "✉️ Gửi lại email hướng dẫn"
- [ ] Redirect về trang với alert thành công
- [ ] Email được gửi lại
- [ ] Click nhiều lần → Rate limit hoạt động (429 error)

#### Test 8: Thanh toán và cập nhật status
- [ ] Thực hiện chuyển khoản test
- [ ] Hệ thống tự động cập nhật status → success
- [ ] Redirect về dashboard
- [ ] Số dư được cộng đúng

---

### 🔒 Test Bảo Mật

#### Test Security 1: QR Proxy HMAC
- [ ] Truy cập: `qr_proxy.php?code=TS12345&sig=invalid` → 403 Forbidden ✅
- [ ] Truy cập: `qr_proxy.php?code=TS12345` → 403/400 ✅
- [ ] Chỉ signature đúng mới trả về QR code

#### Test Security 2: Rate Limiting
- [ ] Reload trang QR nhiều lần (>10 lần trong 1 phút)
- [ ] Sau lần thứ 11 → 429 Too Many Requests ✅
- [ ] Đợi 1 phút → Rate reset, lại request được

#### Test Security 3: View Source Không Lộ Info
- [ ] View Source Code nhiều lần
- [ ] Ctrl+F tìm: số tài khoản → Không tìm thấy ✅
- [ ] Ctrl+F tìm: tên chủ TK → Không tìm thấy ✅
- [ ] Ctrl+F tìm: tên ngân hàng → Không tìm thấy ✅

#### Test Security 4: Browser DevTools
- [ ] F12 → Network tab
- [ ] Reload trang
- [ ] Click vào các requests
- [ ] Response không chứa plaintext bank info ✅

---

### 📊 Monitoring

- [ ] **Check logs sau 24h**
  - [ ] PHP error logs: Không có lỗi critical
  - [ ] Server logs: Response time bình thường
  - [ ] Rate limit logs: Không có abuse pattern

- [ ] **User feedback**
  - [ ] Hỏi vài user test: Có thấy thông tin ngân hàng không? → Yes ✅
  - [ ] Thanh toán có thành công không? → Yes ✅
  - [ ] QR Code có scan được không? → Yes ✅

---

### 🔄 Rollback Plan (Nếu Có Vấn Đề)

- [ ] **Chuẩn bị rollback**
  - [ ] Giữ file backup `pay.php.backup`
  - [ ] Nếu có lỗi nghiêm trọng:
    1. Rename `pay.php` → `pay.php.new`
    2. Rename `pay.php.backup` → `pay.php`
    3. Xóa `qr_proxy.php` (hoặc để lại không sao)
  - [ ] Database không cần rollback (không có thay đổi schema)

---

### 📝 Post-Deployment

- [ ] **Cập nhật documentation**
  - [ ] Ghi chú version mới: v2.0 (Secure+)
  - [ ] Lưu APP_SECRET vào password manager
  - [ ] Note down ngày deploy

- [ ] **Thông báo team**
  - [ ] Thông báo team đã deploy
  - [ ] Share tài liệu `README_NANG_CAP_BAO_MAT.md`
  - [ ] Training về tính năng mới (nếu cần)

- [ ] **Schedule maintenance**
  - [ ] Đặt lịch rotate APP_SECRET (3-6 tháng)
  - [ ] Monitor rate limiting weekly
  - [ ] Review logs monthly

---

### 🎯 Success Criteria

Deployment thành công khi:

- ✅ Trang thanh toán load bình thường
- ✅ Người dùng thấy đầy đủ thông tin trên giao diện
- ✅ QR Code hiển thị và scan được
- ✅ Email gửi thành công
- ✅ **View Source không lộ thông tin ngân hàng**
- ✅ Thanh toán thực tế hoạt động
- ✅ Không có error logs nghiêm trọng

---

## 🚨 Troubleshooting

### Vấn đề: QR không hiển thị

**Nguyên nhân:**
- Signature không đúng
- APP_SECRET chưa set hoặc sai

**Giải pháp:**
1. Check `config.php` có define `APP_SECRET` chưa
2. Check console F12 có lỗi 403/400 không
3. Verify `qr_proxy.php` đã upload đúng chưa

---

### Vấn đề: Thông tin vẫn là `***`

**Nguyên nhân:**
- JavaScript decode lỗi
- APP_SECRET không khớp

**Giải pháp:**
1. F12 → Console → Xem lỗi
2. Verify APP_SECRET giống nhau giữa encode/decode
3. Clear cache browser

---

### Vấn đề: 429 Too Many Requests

**Nguyên nhân:**
- Rate limit đạt tối đa

**Giải pháp:**
- Đợi 1 phút
- Hoặc tăng rate limit trong code (không khuyến khích)

---

## 📞 Liên Hệ Hỗ Trợ

Nếu gặp vấn đề không giải quyết được:

1. Rollback về version cũ
2. Capture screenshots lỗi
3. Copy PHP error logs
4. Gửi thông tin để được hỗ trợ

---

## ✨ Hoàn Thành!

Nếu tất cả checklist đều ✅, chúc mừng bạn đã triển khai thành công hệ thống bảo mật mới!

**Lưu ý cuối:** Đừng quên rotate APP_SECRET định kỳ và monitor logs thường xuyên.

---

**Prepared by:** AI Security Assistant  
**Version:** 2.0  
**Date:** 2025-11-30
