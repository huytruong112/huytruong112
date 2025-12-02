# ✅ Checklist Triển Khai

## 📋 Các file cần upload

### 1. File PHP (3 files)
- [ ] `wireguard_connect.php` → Upload vào root directory
- [ ] `v2box_connect.php` → Upload vào root directory  
- [ ] `manage_services.php` → Upload vào root directory (OVERWRITE file cũ)

### 2. File CSS (2 files)
- [ ] `css/wireguard-connect.css` → Upload vào folder css/
- [ ] `css/v2box-connect.css` → Upload vào folder css/

### 3. File JavaScript (2 files)
- [ ] `js/wireguard-connect.js` → Upload vào folder js/
- [ ] `js/v2box-connect.js` → Upload vào folder js/

## 🔧 Sau khi upload

### 1. Kiểm tra permissions
```bash
chmod 644 *.php
chmod 755 css/
chmod 755 js/
chmod 755 qrcodes/
```

### 2. Kiểm tra thư mục tồn tại
- [ ] Folder `css/` đã tồn tại
- [ ] Folder `js/` đã tồn tại
- [ ] Folder `qrcodes/` đã tồn tại và writable

### 3. Kiểm tra dependencies
- [ ] File `db.php` tồn tại (kết nối database)
- [ ] Thư viện `phpqrcode/qrlib.php` đã cài đặt
- [ ] Bootstrap 5.3.0 CDN accessible
- [ ] Font Awesome 6.5.2 CDN accessible

## 🧪 Testing

### Test trên iOS
- [ ] Mở Safari trên iPhone/iPad
- [ ] Đăng nhập vào hệ thống
- [ ] Vào "Quản Lý Dịch Vụ"
- [ ] Click "Kết nối ngay" ở cột Public Key
- [ ] Kiểm tra WireGuard app tự động mở
- [ ] Xác nhận config được thêm vào

### Test trên Android
- [ ] Mở Chrome trên Android
- [ ] Đăng nhập vào hệ thống
- [ ] Vào "Quản Lý Dịch Vụ"
- [ ] Click "Kết nối ngay" ở cột Public Key
- [ ] Kiểm tra WireGuard app tự động mở
- [ ] Xác nhận config được thêm vào

### Test fallback (chưa cài app)
- [ ] Xóa WireGuard app
- [ ] Click "Kết nối ngay"
- [ ] Kiểm tra tự động chuyển App Store/Play Store
- [ ] Cài app và quay lại
- [ ] Click "Thử lại"
- [ ] Kiểm tra app mở và thêm config

### Test trên Desktop
- [ ] Mở browser trên PC/Mac
- [ ] Đăng nhập vào hệ thống
- [ ] Vào "Quản Lý Dịch Vụ"
- [ ] Click "Kết nối ngay"
- [ ] Kiểm tra hiển thị thông báo hợp lý
- [ ] Kiểm tra QR code hiển thị đúng

## 🎨 Visual Check

### Nút "Kết nối ngay"
- [ ] Hiển thị trong cột Public Key
- [ ] Màu gradient xanh lá - tím
- [ ] Icon plug (🔌) hiển thị
- [ ] Hover effect hoạt động
- [ ] Responsive trên mobile

### Trang wireguard_connect.php
- [ ] Icon WireGuard hiển thị
- [ ] QR Code tạo đúng
- [ ] Public Key hiển thị và copy được
- [ ] Link App Store/Play Store hoạt động
- [ ] Responsive trên mobile
- [ ] Gradient background đẹp

## 🔒 Security Check

- [ ] Kiểm tra session validation
- [ ] Kiểm tra user ownership (chỉ owner xem được config)
- [ ] Kiểm tra SQL injection (PDO prepared statements)
- [ ] Kiểm tra XSS (htmlspecialchars)
- [ ] Kiểm tra file permissions
- [ ] Kiểm tra HTTPS (recommended)

## 📊 Database Check

- [ ] Table `user_services` có cột `qr_data`
- [ ] Table `user_services` có cột `public_key`
- [ ] Table `user_services` có cột `is_activated`
- [ ] Dữ liệu `qr_data` format WireGuard hợp lệ
- [ ] Dữ liệu `public_key` không rỗng

## ⚠️ Troubleshooting

### Nút "Kết nối ngay" không hiển thị
- [ ] Check service status = "Đang Hoạt Động"
- [ ] Check is_activated = 1
- [ ] Check public_key không rỗng
- [ ] Check CSS file đã load

### Deep link không hoạt động
- [ ] Check browser console cho errors
- [ ] Check config encode đúng
- [ ] Check device detection
- [ ] Try QR code thay thế

### QR Code không hiển thị
- [ ] Check folder qrcodes/ writable
- [ ] Check phpqrcode library installed
- [ ] Check qr_data không rỗng
- [ ] Check file path đúng

## 📝 Notes

- Tính năng chỉ hoạt động tốt trên mobile browsers
- Desktop users nên dùng QR Code
- Deep link timeout: 2.5 giây
- Config tự động copy vào clipboard

## ✅ Hoàn tất

Khi tất cả checkboxes đã tích ✓, hệ thống sẵn sàng production!

---

📅 **Date:** _____________
👤 **Tested by:** _____________
✍️ **Signature:** _____________
