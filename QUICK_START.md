# 🚀 Quick Start Guide

## Tóm tắt nhanh

Đã thêm nút **"Kết nối ngay"** vào cột Public Key để tự động kết nối WireGuard VPN chỉ với 1 click.

## 📦 Files cần upload (7 files)

```bash
# 3 PHP files
wireguard_connect.php    → /workspace/
v2box_connect.php        → /workspace/
manage_services.php      → /workspace/ (overwrite)

# 2 CSS files  
css/wireguard-connect.css → /workspace/css/
css/v2box-connect.css     → /workspace/css/

# 2 JS files
js/wireguard-connect.js   → /workspace/js/
js/v2box-connect.js       → /workspace/js/
```

## ⚡ Sử dụng ngay

1. **Upload 7 files** như danh sách trên
2. **Kiểm tra permissions:**
   ```bash
   chmod 755 css/ js/ qrcodes/
   ```
3. **Test trên mobile:**
   - Vào trang "Quản Lý Dịch Vụ"
   - Click nút "🔌 Kết nối ngay" ở cột Public Key
   - WireGuard sẽ tự động mở và thêm config!

## 🎯 Tính năng

✅ Tự động mở WireGuard app  
✅ Tự động thêm config VPN  
✅ Fallback sang App Store/Play Store nếu chưa cài  
✅ Hoạt động trên iOS và Android  
✅ QR Code backup option  
✅ UI/UX đẹp với gradient effects  

## 📱 User Flow

### Đã cài WireGuard (5 giây)
```
Click "Kết nối ngay" → Mở app → Xác nhận → Xong! ✅
```

### Chưa cài WireGuard (2-3 phút)
```
Click "Kết nối ngay" → Chuyển App Store/Play Store 
→ Tải app → Quay lại → Click "Thử lại" → Xác nhận → Xong! ✅
```

## 🎨 Giao diện

**Trong bảng quản lý:**
```
┌─────────────────────────────────────┐
│ Public Key                          │
├─────────────────────────────────────┤
│ [Key content...]                    │
│                                     │
│ [Sao chép] [Tải xuống] [🔌 Kết nối ngay] ← MỚI
└─────────────────────────────────────┘
```

**Trang kết nối:**
- Icon WireGuard với gradient xanh lá - tím
- QR Code để scan thủ công
- Nút "Kết nối ngay" nổi bật
- Public Key với nút copy
- Link App Store & Google Play

## ⚠️ Yêu cầu

- ✅ PHP 7.4+
- ✅ PDO MySQL
- ✅ phpqrcode library
- ✅ Folder `qrcodes/` writable
- ✅ Mobile browser (iOS Safari / Android Chrome)

## 🔧 Troubleshooting

**Nút không hiện?**
→ Check: Dịch vụ = "Đang Hoạt Động", is_activated=1, public_key có giá trị

**App không mở?**
→ Đợi 2.5s sẽ tự chuyển sang App Store/Play Store

**QR không hiện?**
→ Check folder `qrcodes/` có quyền write

## 📚 Tài liệu đầy đủ

- `CHECKLIST.md` - Chi tiết checklist deployment
- `SUMMARY.md` - Tổng quan toàn bộ hệ thống
- `README_WIREGUARD_CONNECT.md` - Tài liệu kỹ thuật

## ✨ That's it!

Upload → Test → Enjoy! 🎉

---

**Câu hỏi?** Đọc `SUMMARY.md` để biết chi tiết hơn.
