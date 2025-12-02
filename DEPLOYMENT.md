# 🚀 Hướng dẫn Deployment

## ⚡ Quick Deploy (3 phút)

### Bước 1: Upload files (4 files)

```bash
# Upload vào /workspace/
wireguard_connect.php
manage_services.php  # OVERWRITE file cũ

# Upload vào /workspace/css/
css/wireguard-connect.css

# Upload vào /workspace/js/
js/wireguard-connect.js
```

### Bước 2: Set permissions

```bash
chmod 644 wireguard_connect.php
chmod 644 manage_services.php
chmod 755 css/
chmod 755 js/
chmod 755 qrcodes/
```

### Bước 3: Test

1. **Mở mobile browser** (iOS Safari hoặc Android Chrome)
2. **Đăng nhập** vào hệ thống
3. **Vào "Quản Lý Dịch Vụ"**
4. **Click nút "🔌 Kết nối ngay"** ở cột Public Key
5. **Verify:** WireGuard app tự động mở

## ✅ Checklist đầy đủ

### Pre-deployment

- [ ] Backup file `manage_services.php` cũ
- [ ] Check PHP version >= 7.4
- [ ] Check PDO extension enabled
- [ ] Check phpqrcode library installed
- [ ] Check folder `qrcodes/` exists và writable

### Upload files

- [ ] Upload `wireguard_connect.php` → `/workspace/`
- [ ] Upload `manage_services.php` → `/workspace/` (overwrite)
- [ ] Upload `css/wireguard-connect.css` → `/workspace/css/`
- [ ] Upload `js/wireguard-connect.js` → `/workspace/js/`

### Set permissions

- [ ] `chmod 644 *.php`
- [ ] `chmod 755 css/`
- [ ] `chmod 755 js/`
- [ ] `chmod 755 qrcodes/`

### Testing - iOS

- [ ] Mở Safari trên iPhone/iPad
- [ ] Đăng nhập và vào "Quản Lý Dịch Vụ"
- [ ] Click "Kết nối ngay" ở dịch vụ active
- [ ] Verify WireGuard tự động mở
- [ ] Verify config xuất hiện trong dialog
- [ ] Xác nhận thêm config
- [ ] Verify config đã được thêm vào WireGuard

**Test Fallback (chưa cài app):**
- [ ] Xóa WireGuard app khỏi iPhone
- [ ] Click "Kết nối ngay"
- [ ] Đợi 2.5s
- [ ] Verify tự động chuyển đến App Store
- [ ] Cài WireGuard từ App Store
- [ ] Quay lại trang web
- [ ] Click "Thử lại"
- [ ] Verify WireGuard mở và thêm config thành công

### Testing - Android

- [ ] Mở Chrome trên Android phone/tablet
- [ ] Đăng nhập và vào "Quản Lý Dịch Vụ"
- [ ] Click "Kết nối ngay" ở dịch vụ active
- [ ] Verify WireGuard tự động mở
- [ ] Verify config xuất hiện trong dialog
- [ ] Xác nhận thêm config
- [ ] Verify config đã được thêm vào WireGuard

**Test Fallback (chưa cài app):**
- [ ] Gỡ WireGuard app khỏi Android
- [ ] Click "Kết nối ngay"
- [ ] Đợi 2.5s
- [ ] Verify tự động chuyển đến Google Play
- [ ] Cài WireGuard từ Google Play
- [ ] Quay lại trang web
- [ ] Click "Thử lại"
- [ ] Verify WireGuard mở và thêm config thành công

### Testing - Desktop

- [ ] Mở browser trên PC/Mac
- [ ] Đăng nhập và vào "Quản Lý Dịch Vụ"
- [ ] Click "Kết nối ngay"
- [ ] Verify hiển thị thông báo "Vui lòng dùng mobile..."
- [ ] Verify QR Code hiển thị đúng
- [ ] Scan QR từ WireGuard app trên mobile
- [ ] Verify config được thêm thành công

### Visual Check

- [ ] Nút "Kết nối ngay" hiển thị với gradient xanh-tím
- [ ] Icon plug (🔌) hiển thị đúng
- [ ] Hover effect hoạt động (nút nổi lên)
- [ ] Button disabled khi đang processing
- [ ] Spinner animation chạy smooth
- [ ] Status messages hiển thị đúng màu
- [ ] QR Code render rõ nét
- [ ] Public Key hiển thị và copy được
- [ ] Responsive trên mọi kích thước màn hình

### Database Check

- [ ] Table `user_services` có column `qr_data`
- [ ] Table `user_services` có column `public_key`
- [ ] Table `user_services` có column `is_activated`
- [ ] Sample data: `qr_data` có format WireGuard đúng
- [ ] Sample data: `public_key` không NULL
- [ ] Sample data: `is_activated` = 1 cho dịch vụ active

### Security Check

- [ ] Session validation hoạt động
- [ ] User chỉ xem được config của mình
- [ ] SQL injection test (thử id=-1, id=abc, etc.)
- [ ] XSS test (thử inject script vào GET params)
- [ ] CSRF token check (nếu có)
- [ ] HTTPS enabled (recommended)

## 🐛 Troubleshooting

### Issue: Nút "Kết nối ngay" không hiển thị

**Check:**
```sql
SELECT id, status, is_activated, public_key 
FROM user_services 
WHERE user_id = YOUR_USER_ID;
```

**Yêu cầu:**
- `status` != 'canceled'
- `is_activated` = 1
- `public_key` IS NOT NULL
- Expiry date > now()

**Fix:**
```sql
UPDATE user_services 
SET is_activated = 1, 
    status = 'active' 
WHERE id = SERVICE_ID;
```

### Issue: WireGuard không tự động mở

**Nguyên nhân:**
1. Browser không support deep link
2. Config encode sai
3. User cancel

**Check browser console:**
```javascript
// F12 > Console
// Tìm errors liên quan đến:
// - window.location.href
// - encodeURIComponent
// - Deep link format
```

**Test manual:**
```javascript
// iOS
window.location.href = 'wireguard://import-profile?contents=BASE64_HERE';

// Android  
window.location.href = 'intent://import-profile?contents=BASE64_HERE#Intent;scheme=wireguard;package=com.wireguard.android;end';
```

**Fix:**
1. Sử dụng Safari (iOS) hoặc Chrome (Android)
2. Check config base64 encode đúng
3. Thử scan QR thay thế

### Issue: Fallback không chuyển sang Store

**Check:**
```javascript
// Trong js/wireguard-connect.js
// Line ~72 (iOS) và ~113 (Android)
// Verify timeout = 2500ms
// Verify store URLs đúng
```

**Test manual:**
```javascript
// iOS
window.location.href = 'https://apps.apple.com/us/app/wireguard/id1441195209';

// Android
window.location.href = 'https://play.google.com/store/apps/details?id=com.wireguard.android';
```

**Fix:**
1. Check network connection
2. Tăng timeout lên 3000ms nếu cần
3. Check popup blocker settings

### Issue: QR Code không hiển thị

**Check folder permissions:**
```bash
ls -la qrcodes/
# Should show: drwxr-xr-x (755)
```

**Check phpqrcode:**
```bash
ls -la /path/to/phpqrcode/qrlib.php
# Should exist
```

**Check database:**
```sql
SELECT qr_data 
FROM user_services 
WHERE id = SERVICE_ID;
-- Should NOT be NULL or empty
```

**Fix:**
```bash
chmod 755 qrcodes/
# or
mkdir qrcodes/
chmod 755 qrcodes/
```

### Issue: Config sai format

**WireGuard config format:**
```ini
[Interface]
PrivateKey = YOUR_PRIVATE_KEY_HERE
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = SERVER_PUBLIC_KEY_HERE
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

**Check trong database:**
```sql
SELECT qr_data 
FROM user_services 
WHERE id = SERVICE_ID;
```

**Validate:**
- Phải có section `[Interface]`
- Phải có section `[Peer]`
- PrivateKey phải là base64
- PublicKey phải là base64
- Endpoint phải là `host:port`

## 📊 Post-Deployment

### Monitor logs

```bash
# PHP errors
tail -f /var/log/php/error.log

# Nginx/Apache access
tail -f /var/log/nginx/access.log

# Specific page
tail -f /var/log/nginx/access.log | grep "wireguard_connect"
```

### Check performance

```bash
# Page load time
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://yourdomain.com/wireguard_connect.php?id=1

# QR generation time
time php -r "require 'phpqrcode/qrlib.php'; QRcode::png('test', 'test.png');"
```

### Monitor user activity

```sql
-- Count successful connections
SELECT COUNT(*) 
FROM access_logs 
WHERE page = 'wireguard_connect' 
  AND date > NOW() - INTERVAL 24 HOUR;

-- Most active users
SELECT user_id, COUNT(*) as connections
FROM access_logs 
WHERE page = 'wireguard_connect'
  AND date > NOW() - INTERVAL 7 DAY
GROUP BY user_id
ORDER BY connections DESC
LIMIT 10;
```

## 🔄 Rollback Plan

Nếu có issues sau deploy:

### Bước 1: Restore backup

```bash
# Restore manage_services.php
cp manage_services.php.backup manage_services.php
```

### Bước 2: Remove new files

```bash
rm wireguard_connect.php
rm css/wireguard-connect.css
rm js/wireguard-connect.js
```

### Bước 3: Clear cache

```bash
# Browser cache
# User: Ctrl+Shift+Delete

# PHP opcache (nếu có)
# Thêm vào PHP:
opcache_reset();
```

### Bước 4: Verify

- [ ] Old functionality works
- [ ] No errors in logs
- [ ] Users can access normally

## ✅ Production Checklist

Trước khi announce feature:

- [ ] ✅ All tests passed
- [ ] ✅ Backups created
- [ ] ✅ Rollback plan ready
- [ ] ✅ Monitoring enabled
- [ ] ✅ Documentation complete
- [ ] ✅ Support team notified
- [ ] ✅ Performance acceptable
- [ ] ✅ Security validated

## 📞 Support Contact

**Technical Issues:**
- Check README.md cho troubleshooting
- Check DEPLOYMENT.md (file này) cho deployment issues

**User Questions:**
- "App không mở?" → Check browser, thử QR
- "Chưa cài app?" → Hướng dẫn tải từ Store
- "Lỗi config?" → Check database qr_data

---

**Ready to deploy!** 🚀
