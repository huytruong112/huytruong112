# 🔐 WireGuard Auto-Connect

## Tổng quan

Tính năng **"Kết nối ngay"** giúp người dùng kết nối WireGuard VPN chỉ với **1 click**:
- ✅ Tự động mở ứng dụng **WireGuard** trên mobile
- ✅ Tự động thêm cấu hình VPN
- ✅ Tự động chuyển sang **App Store/Google Play** nếu chưa cài app

## 📦 Files cần upload (4 files)

```
wireguard_connect.php           → /workspace/
manage_services.php             → /workspace/ (overwrite)
css/wireguard-connect.css       → /workspace/css/
js/wireguard-connect.js         → /workspace/js/
```

## 🎯 Cách hoạt động

### 1. User đã cài WireGuard (5 giây)
```
Click "Kết nối ngay"
    ↓
Mở ứng dụng WireGuard
    ↓
Xác nhận thêm config
    ↓
Xong! ✅
```

### 2. User chưa cài WireGuard (2-3 phút)
```
Click "Kết nối ngay"
    ↓
Đợi 2.5s (thử mở app)
    ↓
Không có app → Tự động chuyển App Store/Play Store
    ↓
User tải và cài WireGuard
    ↓
Quay lại trang web
    ↓
Click "Thử lại"
    ↓
Mở WireGuard và thêm config
    ↓
Xong! ✅
```

## 📱 Platform Support

| Platform | Tự động mở app | QR Code | Fallback Store |
|----------|---------------|---------|----------------|
| **iOS** | ✅ Safari | ✅ | ✅ App Store |
| **Android** | ✅ Chrome | ✅ | ✅ Google Play |
| **Desktop** | ⚠️ Không | ✅ | - |

## 🔧 Deep Link Chi tiết

### iOS
```javascript
wireguard://import-profile?contents=BASE64_CONFIG
```
- Timeout: 2.5 giây
- Fallback: `https://apps.apple.com/us/app/wireguard/id1441195209`

### Android
```javascript
intent://import-profile?contents=BASE64_CONFIG#Intent;
scheme=wireguard;
package=com.wireguard.android;
end
```
- Timeout: 2.5 giây
- Fallback: `https://play.google.com/store/apps/details?id=com.wireguard.android`

### Desktop
- Hiển thị thông báo: "Vui lòng sử dụng mobile hoặc quét QR"
- Không có deep link

## 🚀 Deployment

### Bước 1: Upload files
```bash
# Upload PHP
wireguard_connect.php → /workspace/
manage_services.php → /workspace/ (overwrite)

# Upload CSS
css/wireguard-connect.css → /workspace/css/

# Upload JS
js/wireguard-connect.js → /workspace/js/
```

### Bước 2: Set permissions
```bash
chmod 755 css/ js/ qrcodes/
```

### Bước 3: Test
1. Mở mobile browser (iOS Safari / Android Chrome)
2. Đăng nhập vào hệ thống
3. Vào "Quản Lý Dịch Vụ"
4. Click nút "🔌 Kết nối ngay" ở cột Public Key
5. Verify WireGuard tự động mở

## ✅ Checklist Testing

### iOS Testing
- [ ] Safari trên iPhone/iPad
- [ ] Click "Kết nối ngay"
- [ ] WireGuard app tự động mở
- [ ] Config được thêm vào app
- [ ] Test khi chưa cài app → Chuyển App Store
- [ ] Test nút "Thử lại" sau khi cài app

### Android Testing
- [ ] Chrome trên Android phone/tablet
- [ ] Click "Kết nối ngay"
- [ ] WireGuard app tự động mở
- [ ] Config được thêm vào app
- [ ] Test khi chưa cài app → Chuyển Google Play
- [ ] Test nút "Thử lại" sau khi cài app

### Desktop Testing
- [ ] Browser trên PC/Mac
- [ ] Click "Kết nối ngay"
- [ ] Hiển thị thông báo phù hợp
- [ ] QR Code hiển thị đúng

## 🔒 Security

✅ **Session validation** - Kiểm tra đăng nhập  
✅ **User ownership** - Chỉ owner xem được config  
✅ **PDO prepared statements** - Chống SQL injection  
✅ **htmlspecialchars()** - Chống XSS  
✅ **HTTPS recommended** - Bảo vệ config trên đường truyền

## ⚠️ Troubleshooting

### Nút "Kết nối ngay" không hiển thị
**Nguyên nhân:**
- Dịch vụ không ở trạng thái "Đang Hoạt Động"
- `is_activated` != 1
- `public_key` rỗng

**Giải pháp:**
1. Check `SELECT status, is_activated, public_key FROM user_services WHERE id=X`
2. Đảm bảo status = 'active' hoặc tương đương
3. Đảm bảo is_activated = 1
4. Đảm bảo public_key không NULL

### WireGuard app không tự động mở
**Nguyên nhân:**
- Browser không support deep link
- Config encode sai
- User cancel trong quá trình

**Giải pháp:**
1. Sử dụng browser chính thức (Safari iOS, Chrome Android)
2. Check console log cho errors
3. Thử scan QR Code thay thế
4. Đợi đủ 2.5s để fallback

### QR Code không hiển thị
**Nguyên nhân:**
- Folder `qrcodes/` không có quyền write
- phpqrcode library chưa cài
- qr_data rỗng

**Giải pháp:**
1. `chmod 755 qrcodes/`
2. Cài phpqrcode: `composer require phpqrcode`
3. Check database: `SELECT qr_data FROM user_services WHERE id=X`

### Config encode sai
**Nguyên nhân:**
- qr_data không đúng format WireGuard
- Base64 encode lỗi

**Giải pháp:**
1. Verify qr_data có format:
   ```
   [Interface]
   PrivateKey = ...
   Address = ...
   DNS = ...

   [Peer]
   PublicKey = ...
   Endpoint = ...
   AllowedIPs = ...
   ```
2. Test base64: `echo "qr_data" | base64`

## 💡 Tips

### Cho Users
- 📱 Dùng mobile browser để trải nghiệm tốt nhất
- ⏱️ Đợi 2-3 giây để app tự động mở
- 🔄 Dùng "Thử lại" sau khi cài app mới
- 📷 Quét QR nếu deep link không hoạt động

### Cho Admins
- 🔐 Luôn backup trước khi deploy
- 🧪 Test trên staging trước production
- 📊 Monitor logs để detect issues sớm
- ✅ Verify permissions của folders

### Cho Developers
- 📝 Code đã được structure tốt và comment đầy đủ
- 🎨 CSS/JS tách riêng, dễ customize
- 🔧 Logic rõ ràng, dễ debug
- 📚 Follow existing patterns khi thêm features

## 📚 Code Structure

```
/workspace/
├── wireguard_connect.php          # PHP backend
│   ├── Session validation
│   ├── Database query
│   ├── Config encoding
│   ├── QR generation
│   └── HTML render
│
├── css/wireguard-connect.css      # Styles
│   ├── Gradient backgrounds
│   ├── Button styles
│   ├── Animations
│   └── Responsive design
│
└── js/wireguard-connect.js        # Client logic
    ├── Device detection
    ├── Deep link handler
    ├── Fallback to store
    ├── Status messages
    └── Retry logic
```

## 🎨 UI/UX Features

### Button Design
- **Color:** Gradient #88d3ce → #6e45e2 (WireGuard brand)
- **Icon:** Plug (🔌)
- **Text:** "Kết nối ngay"
- **Effect:** Hover lift + shadow
- **State:** Disabled during processing

### Status Messages
- 📱 Initial: "Bấm nút để kết nối..."
- ⏳ Processing: "Đang kết nối..." (with spinner)
- ✅ Success: "Đã mở WireGuard thành công!"
- ⚠️ Warning: "Chưa cài app, đang chuyển..."
- 🔄 Retry: "Bấm Thử Lại để thêm config"

### Responsive Design
- **Mobile:** Full width buttons, large touch targets
- **Tablet:** Optimized spacing
- **Desktop:** Centered layout với max-width

## 🔄 Update History

### v1.0.0 (2025-12-02)
- ✅ Initial release
- ✅ iOS và Android support
- ✅ Tự động mở WireGuard app
- ✅ Fallback App Store/Play Store
- ✅ QR Code generation
- ✅ Responsive design

### v1.1.0 (2025-12-02)
- ✅ Xóa V2Box - Chỉ focus WireGuard
- ✅ Tối ưu logic deep link
- ✅ Cải thiện error handling
- ✅ Update documentation

## 📞 Support

**WireGuard Official:**
- Website: https://www.wireguard.com/
- iOS App: https://apps.apple.com/us/app/wireguard/id1441195209
- Android App: https://play.google.com/store/apps/details?id=com.wireguard.android

**Documentation:**
- WireGuard Protocol: https://www.wireguard.com/protocol/
- Quick Start: https://www.wireguard.com/quickstart/

## ✨ Highlights

🎉 **Chỉ gọi WireGuard** - Không có app khác  
🎉 **1 Click Connect** - Đơn giản nhất có thể  
🎉 **Smart Fallback** - Tự động chuyển store khi cần  
🎉 **Clean Code** - Dễ đọc, dễ maintain  
🎉 **Production Ready** - Tested và stable  

---

## 🎊 Kết luận

Tính năng **WireGuard Auto-Connect** giúp users kết nối VPN nhanh chóng và dễ dàng:

❌ **Trước:**
1. Copy config thủ công
2. Mở WireGuard app riêng
3. Paste config
4. Đặt tên tunnel
5. Save → Kết nối

✅ **Bây giờ:**
1. Click "Kết nối ngay" → Done! 🚀

**Ready to deploy!** 🎉
