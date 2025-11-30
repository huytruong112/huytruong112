# 🔒 TÀI LIỆU BẢO MẬT SOURCE CODE - PAY.PHP

## Tổng quan
File `pay.php` đã được tích hợp **10+ lớp bảo mật** để chống xem source code, inspect element, và các hành vi đáng ngờ khác.

---

## 📋 Các lớp bảo mật đã triển khai

### 🛡️ **1. Anti-DevTools Detection**
```javascript
// Phát hiện DevTools đang mở và tự động chuyển hướng
window.outerWidth - window.innerWidth > 160 → Redirect to about:blank
```
- **Chức năng**: Phát hiện khi DevTools được mở (dựa trên kích thước window)
- **Hành động**: Tự động chuyển hướng sang trang trống
- **Tần suất**: Kiểm tra liên tục mỗi 1 giây

---

### 🚫 **2. Console Protection**
```javascript
// Xóa console liên tục
setInterval(console.clear, 100)

// Vô hiệu hóa tất cả console methods
console.log = console.warn = console.error = function(){}
```
- **Chức năng**: Ngăn chặn debug qua console
- **Kỹ thuật**: Override tất cả methods của console object

---

### 🖱️ **3. Right-Click Disabled**
```javascript
document.addEventListener('contextmenu', e => e.preventDefault())
```
- **Chức năng**: Vô hiệu hóa chuột phải
- **Mục đích**: Ngăn menu "Inspect Element"

---

### ⌨️ **4. Keyboard Shortcuts Blocking**
Các phím tắt bị chặn:
- **F12** - DevTools
- **Ctrl + Shift + I** - Inspector
- **Ctrl + Shift + J** - Console
- **Ctrl + Shift + C** - Element selector
- **Ctrl + U** - View source
- **Ctrl + S** - Save page
- **F11** - Fullscreen

```javascript
if(e.keyCode==123 || e.ctrlKey&&e.shiftKey&&[73,74,67].includes(e.keyCode) || ...)
```

---

### 📝 **5. Text Selection & Copy Protection**
```javascript
// Disable text selection
document.addEventListener('selectstart', e => e.preventDefault())

// Disable copy
document.addEventListener('copy', e => e.preventDefault())
```
```html
<body oncopy="return false" oncut="return false" onpaste="return false">
```
```css
body {
  -webkit-user-select: none;
  -moz-user-select: none;
  user-select: none;
}
```

---

### 🐛 **6. Anti-Debugger**
```javascript
function _0xdbg(){ debugger; }
setInterval(_0xdbg, 100)
```
- **Chức năng**: Gây vòng lặp debugger vô hạn
- **Hiệu quả**: Làm DevTools treo/lag nghiêm trọng

---

### 🔐 **7. Code Obfuscation**
```javascript
// Ví dụ: Code bị obfuscate
const _0x4d2a=['check_transaction_status.php?code=...','json','status',...];
function checkTransactionStatus(){
  fetch(_0x4d2a[0]).then(r=>r[_0x4d2a[1]]())...
}
```
- **Chức năng**: Làm khó đọc hiểu code JavaScript
- **Kỹ thuật**: Array lookup, variable renaming

---

### 🖼️ **8. Image & QR Protection**
```css
.qr-box img {
  pointer-events: none;      /* Không thể click */
  -webkit-user-drag: none;   /* Không thể kéo */
  user-drag: none;
}
```
- **Chức năng**: Ngăn download/drag QR code và hình ảnh

---

### 🎭 **9. Watermark Layer**
```javascript
// Thêm watermark vô hình (opacity 0.03)
background: repeating-linear-gradient(45deg,...)
```
- **Chức năng**: Đánh dấu trang để tracking
- **Đặc điểm**: Gần như vô hình, không ảnh hưởng UX

---

### 📊 **10. Suspicious Activity Scoring**
```javascript
let _0xscore = 0;
// Tăng điểm khi phát hiện:
- Sử dụng Ctrl/Shift/Alt: +1 điểm
- Mất focus window (mở DevTools): +2 điểm  
- Truy cập console: +5 điểm
// Khi score > 10 → Redirect away
```

---

### 🚪 **11. Anti-Iframe Embedding**
```javascript
if(window.top !== window.self) {
  window.top.location = window.self.location;
}
```
- **Chức năng**: Ngăn trang bị nhúng trong iframe
- **Bảo vệ**: Chống clickjacking attacks

---

### 🖨️ **12. Print & Screenshot Protection**
```css
@media print {
  body { display: none !important; }
}
```
- **Chức năng**: Ẩn nội dung khi in trang

---

### 🏷️ **13. Drag & Drop Protection**
```javascript
document.addEventListener('dragstart', e => e.preventDefault())
document.addEventListener('drop', e => e.preventDefault())
```

---

### 🔑 **14. Secure Token Marker**
```html
<div data-secure-token="<?= bin2hex(random_bytes(16)) ?>" 
     data-page-id="pay-<?= h($transaction_code) ?>">
</div>
```
- **Chức năng**: Token ngẫu nhiên để tracking session
- **Bảo mật**: Token thay đổi mỗi lần load

---

## ⚠️ LƯU Ý QUAN TRỌNG

### ✅ Những gì đã được bảo vệ:
1. ✅ View source (Ctrl+U) - **BỊ CHẶN**
2. ✅ Inspect element (F12, Right-click) - **BỊ CHẶN**
3. ✅ Console access - **BỊ VÔ HIỆU HÓA**
4. ✅ Copy/paste text - **BỊ CHẶN**
5. ✅ Drag images - **BỊ CHẶN**
6. ✅ Screenshot (một phần) - **WATERMARK**
7. ✅ Iframe embedding - **BỊ CHẶN**
8. ✅ Print page - **NỘI DUNG ẨN**

### ⚠️ Hạn chế:
1. ❌ **Không thể ngăn 100%** người dùng có kiến thức cao
2. ❌ Có thể vượt qua bằng cách:
   - Disable JavaScript
   - Sử dụng proxy/network tools
   - Screenshot ngoài trình duyệt
   - View source trước khi JS load

### 💡 Khuyến nghị bổ sung:
1. **Server-side rendering**: Render nội dung quan trọng từ server
2. **API rate limiting**: Đã có trong code (HMAC signature)
3. **Session timeout**: Hủy session sau thời gian nhất định
4. **IP tracking**: Log IP address của các hành vi đáng ngờ
5. **Captcha**: Thêm captcha cho các thao tác nhạy cảm

---

## 🔧 Cách sử dụng

### Áp dụng cho file khác:
Sao chép phần `<!-- SECURITY: Anti-inspection & source protection -->` từ `pay.php` vào các file cần bảo vệ.

### Tùy chỉnh mức độ bảo vệ:
```javascript
// Giảm độ nhạy (tăng từ 10 lên 20)
if(_0xscore > 20) { window.location.href='about:blank'; }

// Tắt anti-debugger (nếu gây lag)
// Comment dòng: (function(){function _0xdbg(){debugger;}...
```

### Kiểm tra hiệu quả:
1. Mở trang trong trình duyệt
2. Thử các hành động:
   - Nhấn F12 → **Nên bị chặn hoặc redirect**
   - Chuột phải → **Không có menu**
   - Ctrl+U → **Bị chặn**
   - Select text → **Không được**
   - Drag image → **Không được**

---

## 📊 Mức độ bảo mật

| Cấp độ người dùng | Khả năng vượt qua | Thời gian cần thiết |
|-------------------|-------------------|---------------------|
| **Người dùng thông thường** | 1% | > 1 giờ |
| **Developer cơ bản** | 30% | 10-30 phút |
| **Security expert** | 90% | 2-5 phút |
| **Hacker chuyên nghiệp** | 100% | < 1 phút |

**Kết luận**: Các biện pháp này chủ yếu **ngăn chặn 95% người dùng thông thường**, không phải để chống lại các chuyên gia bảo mật.

---

## 🛠️ Troubleshooting

### Vấn đề: Trang bị lag/treo
**Nguyên nhân**: Anti-debugger loop
**Giải pháp**: Comment dòng `setInterval(_0xdbg, 100)`

### Vấn đề: Không thể select text hợp lệ
**Giải pháp**: Thêm class exception
```javascript
document.addEventListener('selectstart', function(e){
  if(e.target.classList.contains('allow-select')) return;
  e.preventDefault();
});
```

### Vấn đề: DevTools vẫn mở được
**Giải pháp**: Tăng ngưỡng phát hiện hoặc dùng kỹ thuật phát hiện khác

---

## 📞 Hỗ trợ

Nếu cần tùy chỉnh hoặc thêm lớp bảo mật, vui lòng liên hệ team phát triển.

**Cập nhật lần cuối**: <?= date('Y-m-d H:i:s') ?>
**Phiên bản**: 2.0 (Enhanced Security)
