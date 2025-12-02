# Tính năng Kết nối WireGuard tự động

## 📋 Tổng quan

Đã thêm tính năng "Kết nối ngay" cho WireGuard VPN vào cột Public Key trong bảng quản lý dịch vụ. Khi người dùng bấm nút này, hệ thống sẽ:

1. **Tự động mở ứng dụng WireGuard** trên điện thoại (iOS/Android)
2. **Tự động thêm cấu hình VPN** vào WireGuard
3. **Tự động chuyển sang App Store/Google Play** nếu chưa cài đặt ứng dụng

## 📁 Cấu trúc file mới

```
/workspace/
├── wireguard_connect.php           # File PHP xử lý kết nối WireGuard
├── manage_services.php             # Đã cập nhật - thêm nút "Kết nối ngay"
├── css/
│   └── wireguard-connect.css      # CSS cho giao diện WireGuard
└── js/
    └── wireguard-connect.js       # JavaScript xử lý deep link WireGuard
```

## 🎯 Các thay đổi chính

### 1. File `manage_services.php`

**Thay đổi trong cột Public Key:**

```php
<!-- TRƯỚC ĐÂY -->
<button class="copy-btn" onclick="copyBlock('pk...')">
  <i class="fa fa-copy"></i> Sao chép
</button>
<a class="copy-btn" href="download_public_key.php?service_id=...">
  <i class="fa fa-download"></i> Tải xuống
</a>

<!-- SAU KHI CẬP NHẬT -->
<div class="wg-action-buttons">
  <button class="copy-btn" onclick="copyBlock('pk...')">
    <i class="fa fa-copy"></i> Sao chép
  </button>
  <a class="copy-btn" href="download_public_key.php?service_id=...">
    <i class="fa fa-download"></i> Tải xuống
  </a>
  <!-- NÚT MỚI -->
  <a class="btn-connect-wg" href="wireguard_connect.php?id=...">
    <i class="fa fa-plug"></i> Kết nối ngay
  </a>
</div>
```

**CSS mới được thêm:**
```css
.btn-connect-wg {
  background: linear-gradient(135deg, #88d3ce 0%, #6e45e2 100%);
  color: white;
  /* ... */
}
```

### 2. File `wireguard_connect.php`

**Chức năng:**
- Lấy thông tin WireGuard config từ database
- Tạo QR Code cho config
- Hiển thị giao diện kết nối đẹp mắt
- Truyền config cho JavaScript để xử lý deep link

**Logic:**
```php
// Lấy service info
$sql = "SELECT us.id, us.qr_data, us.public_key, sp.package_name
        FROM user_services us
        JOIN service_packages sp ON us.package_id = sp.id
        WHERE us.id = ? AND us.user_id = ?";

// Encode config
$configBase64 = base64_encode($qrData);

// Truyền cho JS
initializeWireGuardConfig(
    <?= json_encode($qrData) ?>,
    <?= json_encode($configBase64) ?>,
    <?= json_encode($publicKey) ?>
);
```

### 3. File `js/wireguard-connect.js`

**Deep Link cho iOS:**
```javascript
const deepLink = `wireguard://import-profile?contents=${encodeURIComponent(wgConfigBase64)}`;
window.location.href = deepLink;
```

**Deep Link cho Android:**
```javascript
const intent = `intent://import-profile?contents=${encodeURIComponent(wgConfigBase64)}#Intent;scheme=wireguard;package=com.wireguard.android;end`;
window.location.href = intent;
```

**Fallback khi chưa cài app:**
```javascript
setTimeout(() => {
    if (!appOpened && !document.hidden) {
        // Chuyển sang App Store hoặc Google Play
        window.location.href = appStoreUrl; // hoặc playStoreUrl
    }
}, 2500);
```

## 🔄 Luồng hoạt động

```
1. User click "Kết nối ngay" trong bảng quản lý dịch vụ
                    ↓
2. Chuyển đến wireguard_connect.php?id=X
                    ↓
3. PHP lấy config từ database và encode
                    ↓
4. JavaScript nhận config và phát hiện thiết bị
                    ↓
5a. iOS: Mở wireguard://import-profile?contents=...
5b. Android: Mở intent://... với package=com.wireguard.android
                    ↓
6a. Đã cài WireGuard → Tự động mở app và thêm config
6b. Chưa cài → Chuyển đến App Store / Google Play
                    ↓
7. User xác nhận thêm config trong app WireGuard
```

## 📱 Giao diện

### Trang kết nối WireGuard

- **Header:** Icon WireGuard với gradient màu xanh lá - tím
- **QR Code:** Hiển thị để scan thủ công nếu cần
- **Nút "Kết Nối Ngay":** Gradient button nổi bật
- **Public Key:** Hiển thị với nút copy
- **Hướng dẫn:** Chi tiết cách sử dụng
- **Link App Store/Play Store:** Direct link để tải app

### Trong bảng quản lý dịch vụ

- Nút "Kết nối ngay" có:
  - Icon plug (⚡)
  - Gradient background màu WireGuard (xanh lá - tím)
  - Hover effect đẹp mắt
  - Responsive trên mobile

## ✅ Tính năng

- ✅ Tự động phát hiện iOS/Android
- ✅ Deep link mở WireGuard app
- ✅ Fallback sang App Store/Play Store
- ✅ Copy config vào clipboard tự động
- ✅ Hiển thị status messages
- ✅ QR Code backup option
- ✅ Retry button sau khi cài app
- ✅ Responsive design
- ✅ Giữ nguyên 100% logic cũ

## 🎨 Design

**Màu sắc:**
- Primary gradient: `#88d3ce` → `#6e45e2` (Xanh lá → Tím WireGuard)
- Success: `#d4edda`
- Warning: `#fff3cd`

**Font:**
- Headers: Montserrat, bold
- Body: Segoe UI, Roboto

**Icons:**
- Font Awesome 6.5.2
- Shield icon cho WireGuard

## 🔒 Bảo mật

- ✅ Session validation
- ✅ User ownership check
- ✅ SQL injection prevention (PDO prepared statements)
- ✅ XSS prevention (htmlspecialchars)
- ✅ Config chỉ accessible bởi owner

## 📲 App Links

**iOS:**
- App Store: https://apps.apple.com/us/app/wireguard/id1441195209
- Deep link: `wireguard://import-profile?contents=<base64>`

**Android:**
- Google Play: https://play.google.com/store/apps/details?id=com.wireguard.android
- Deep link: `intent://... package=com.wireguard.android`

## 🚀 Cách sử dụng

1. Upload 3 file mới lên server:
   - `wireguard_connect.php`
   - `css/wireguard-connect.css`
   - `js/wireguard-connect.js`

2. Upload file cập nhật:
   - `manage_services.php`

3. Kiểm tra permissions:
   - Folder `css/` và `js/` phải readable
   - Folder `qrcodes/` phải writable

4. Test trên mobile device (iOS hoặc Android)

## 🐛 Troubleshooting

**Nút không hiện:**
- Kiểm tra status dịch vụ = "Đang Hoạt Động"
- Kiểm tra `is_activated = 1`
- Kiểm tra `public_key` không rỗng

**Deep link không hoạt động:**
- Kiểm tra config được encode đúng
- Kiểm tra browser support (Safari iOS, Chrome Android)
- Thử quét QR Code thay thế

**App không mở:**
- Đợi 2.5s để redirect sang App Store/Play Store
- Cài app và click "Thử Lại"

## 📝 Notes

- Tính năng chỉ hoạt động trên mobile browsers
- Desktop users nên quét QR Code
- Config được copy vào clipboard tự động
- Deep link timeout: 2.5 giây
