# 🚀 HƯỚNG DẪN SỬ DỤNG BẢO MẬT SOURCE CODE

## ⚡ Quick Start

### Cách 1: Sử dụng code đã được tích hợp sẵn trong pay.php
File `pay.php` hiện tại đã có **tất cả các biện pháp bảo mật** được tích hợp sẵn. Không cần làm gì thêm!

✅ **Kiểm tra**: Mở `pay.php` trong trình duyệt và thử:
- Nhấn F12 → Trang sẽ bị redirect
- Chuột phải → Không có menu
- Ctrl+U → Bị chặn

---

### Cách 2: Sử dụng file config tùy chỉnh (Nâng cao)

#### Bước 1: Include file config
Thêm vào `<head>` của file cần bảo vệ:

```html
<script src="security-config.js"></script>
```

#### Bước 2: Tùy chỉnh config (tuỳ chọn)
Chỉnh sửa `security-config.js`:

```javascript
const SECURITY_CONFIG = {
  // Tắt anti-debugger nếu gây lag
  ANTI_DEBUGGER: {
    enabled: false,  // Đổi thành false
  },
  
  // Tăng ngưỡng suspicious score
  SUSPICIOUS_ACTIVITY: {
    enabled: true,
    scoreThreshold: 20,  // Đổi từ 10 thành 20
  }
};
```

---

## 🎯 Áp dụng cho các file khác

### File HTML thuần
Copy phần bảo mật từ `pay.php` (dòng 473-510):

```html
<!DOCTYPE html>
<html>
<head>
  <title>Your Page</title>
  
  <!-- COPY PHẦN NÀY -->
  <script>
    // Anti-DevTools Detection
    (function(){...})();
    
    // Console Protection
    setInterval(function(){console.clear();},100);
    
    // Disable right-click
    document.addEventListener('contextmenu',e=>e.preventDefault());
    
    // ... (copy tất cả script security)
  </script>
  
  <style>
    body {
      -webkit-user-select: none;
      user-select: none;
    }
    /* ... copy các style khác ... */
  </style>
</head>
<body oncopy="return false">
  <!-- Nội dung của bạn -->
</body>
</html>
```

### File PHP khác
```php
<?php
// Code PHP của bạn
?>
<!DOCTYPE html>
<html>
<head>
  <?php include 'security-header.php'; ?>
  <!-- Hoặc copy trực tiếp từ pay.php -->
</head>
<body>
  <?php include 'your-content.php'; ?>
  <?php include 'security-footer.php'; ?>
</body>
</html>
```

---

## 🔧 Cấu hình cho các trường hợp cụ thể

### Trường hợp 1: Trang cần cho phép select text
```javascript
// Tắt copy protection
COPY_PROTECTION: {
  enabled: false,  // hoặc
  disableSelection: false,
}
```

Hoặc cho phép select cho một số phần tử cụ thể:
```javascript
document.addEventListener('selectstart', function(e){
  // Cho phép select trong các element có class 'selectable'
  if(e.target.classList.contains('selectable')) return;
  e.preventDefault();
});
```

```html
<p class="selectable">Nội dung này có thể select được</p>
<p>Nội dung này KHÔNG thể select</p>
```

### Trường hợp 2: Trang bị lag/chậm
```javascript
// Tắt anti-debugger
ANTI_DEBUGGER: {
  enabled: false,
}

// Tăng interval của console clear
CONSOLE_PROTECTION: {
  enabled: true,
  clearInterval: 500,  // Tăng từ 100 lên 500ms
}
```

### Trường hợp 3: Chỉ bảo vệ một phần trang
```html
<div class="public-content">
  <!-- Nội dung công khai, không cần bảo vệ -->
  <p>Thông tin chung...</p>
</div>

<div class="protected-content" id="secure-area">
  <!-- Nội dung cần bảo vệ -->
  <p>Thông tin nhạy cảm...</p>
</div>

<script>
// Chỉ apply bảo vệ cho #secure-area
document.querySelector('#secure-area').addEventListener('contextmenu', e => e.preventDefault());
</script>
```

### Trường hợp 4: Bật debug mode khi develop
```javascript
const SECURITY_CONFIG = {
  // Bật debug mode = TẮT TẤT CẢ bảo mật
  DEBUG_MODE: true,  // Nhớ đổi thành false khi deploy production!
  // ...
};
```

---

## 📊 Kiểm tra hiệu quả

### Checklist kiểm tra thủ công:
- [ ] F12 không mở được DevTools (hoặc bị redirect)
- [ ] Ctrl+Shift+I không mở được Inspector
- [ ] Ctrl+U không view source được
- [ ] Chuột phải không có menu
- [ ] Không thể select text
- [ ] Không thể copy text
- [ ] Không thể kéo hình ảnh
- [ ] Console bị clear liên tục
- [ ] Trang không thể nhúng trong iframe

### Test tự động (dành cho developer):
```javascript
// Mở console (nếu có thể) và chạy:
console.log('TEST 1: Console working?'); // Nếu thấy text này = console chưa bị disable
console.table([1,2,3]); // Nếu thấy table = console chưa bị disable

// Test select
const selection = window.getSelection().toString();
console.log('TEST 2: Selection:', selection); // Nếu có text = selection chưa bị block

// Test DevTools
console.log('Window size:', window.outerWidth - window.innerWidth);
// Nếu > 160 mà chưa redirect = anti-devtools chưa hoạt động
```

---

## ⚠️ Lưu ý khi deploy Production

### ✅ PHẢI LÀM:
1. **Tắt DEBUG_MODE**:
   ```javascript
   DEBUG_MODE: false,
   ```

2. **Minify JavaScript**: Nén code để khó đọc hơn
   ```bash
   # Sử dụng công cụ minify
   npm install -g terser
   terser security-config.js -o security-config.min.js -c -m
   ```

3. **Enable HTTPS**: Bảo mật chỉ hiệu quả khi dùng HTTPS
   ```apache
   # .htaccess
   RewriteEngine On
   RewriteCond %{HTTPS} off
   RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
   ```

4. **Kiểm tra lại tất cả các tính năng**

### ❌ KHÔNG NÊN:
1. ❌ Để DEBUG_MODE = true trong production
2. ❌ Sử dụng console.log() trong production code
3. ❌ Tin tưởng 100% vào bảo mật client-side
4. ❌ Để thông tin nhạy cảm (password, API key) trong JavaScript

---

## 🐛 Troubleshooting

### Vấn đề: Trang tự động redirect sang about:blank
**Nguyên nhân**: Anti-DevTools đang phát hiện DevTools
**Giải pháp**:
```javascript
// Tắt tạm trong lúc develop
ANTI_DEVTOOLS: { enabled: false }

// Hoặc tăng threshold
ANTI_DEVTOOLS: { threshold: 300 }
```

### Vấn đề: Không thể select text hợp lệ
**Giải pháp**:
```javascript
// Tắt copy protection
COPY_PROTECTION: { disableSelection: false }

// Hoặc cho phép select cho một số element
<div class="allow-select">Text có thể select</div>
```

### Vấn đề: Trang bị lag nghiêm trọng
**Nguyên nhân**: Anti-debugger hoặc console clear quá nhanh
**Giải pháp**:
```javascript
ANTI_DEBUGGER: { enabled: false },
CONSOLE_PROTECTION: { clearInterval: 500 }
```

### Vấn đề: Vẫn xem được source code
**Giải pháp**: Không thể chặn 100%. Các biện pháp này chỉ làm khó hơn:
- Disable JavaScript → Vẫn xem được HTML tĩnh
- Network tab → Vẫn xem được request/response
- Screenshot → Vẫn chụp được màn hình

**Khuyến nghị**: Đừng đặt thông tin nhạy cảm trong HTML/JS!

---

## 📈 Nâng cao: Kết hợp với bảo mật server-side

### 1. Rate Limiting
```php
// Đã có sẵn trong pay.php
if (rate_limited('action_'.$user_id, 5, 60)) {
    http_response_code(429);
    die('Too many requests');
}
```

### 2. HMAC Signature
```php
// Đã có sẵn trong pay.php
$sig = hmac_sign('action|data|userId');
if (!hmac_verify($payload, $sig)) {
    die('Invalid signature');
}
```

### 3. Session Security
```php
// Thêm vào đầu file
ini_set('session.cookie_httponly', 1);
ini_set('session.cookie_secure', 1);  // Chỉ khi dùng HTTPS
ini_set('session.cookie_samesite', 'Strict');
session_start();
```

### 4. Content Security Policy
```php
// Đã có sẵn trong pay.php
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline';");
```

### 5. IP Logging
```php
// Thêm vào file log
function log_suspicious_activity($action) {
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $log = date('Y-m-d H:i:s') . " - IP: $ip - Action: $action\n";
    file_put_contents('security.log', $log, FILE_APPEND);
}
```

---

## 📚 Tài nguyên tham khảo

### Tools kiểm tra bảo mật:
- **Chrome DevTools**: Kiểm tra xem có mở được không
- **View Source**: Ctrl+U hoặc view-source:URL
- **Network Tab**: Kiểm tra requests
- **Console**: Kiểm tra xem có log được không

### Best practices:
1. **Defense in Depth**: Nhiều lớp bảo vệ
2. **Server-side validation**: Luôn validate ở server
3. **HTTPS only**: Bắt buộc dùng HTTPS
4. **Regular updates**: Cập nhật thường xuyên
5. **Security audit**: Kiểm tra định kỳ

---

## 💡 Tips & Tricks

### Tip 1: Sử dụng CDN để cache JavaScript
```html
<script src="https://cdn.yourdomain.com/security-config.min.js"></script>
```

### Tip 2: Dynamic loading để tránh cache
```html
<script src="security-config.js?v=<?= time() ?>"></script>
```

### Tip 3: Obfuscate thêm với base64
```javascript
eval(atob('dmFyIF8weDVhMmI9Wy4uLl0=')); // Obfuscated code
```

### Tip 4: Thêm fake code để đánh lừa
```javascript
// Fake API endpoint (không tồn tại)
const API_KEY = 'fake-key-12345';
const API_ENDPOINT = 'https://fake-api.com/v1/data';

// Real code được obfuscate ở dưới
const _0x4d2a = ['real-endpoint.php'...];
```

---

## 🔐 Kết luận

**Nhớ rằng**: 
- ✅ Client-side security chỉ là một lớp bảo vệ
- ✅ Luôn kết hợp với server-side security
- ✅ Không để thông tin nhạy cảm trong client code
- ✅ Sử dụng HTTPS là bắt buộc
- ✅ Cập nhật và kiểm tra thường xuyên

**Good luck! 🚀**
