# Cấu trúc File V2Box Connect

## 📁 Cấu trúc thư mục

```
/workspace/
├── css/
│   └── v2box-connect.css    # File CSS cho giao diện V2Box
├── js/
│   └── v2box-connect.js     # File JavaScript xử lý logic kết nối
└── v2box_connect.php         # File PHP chính xử lý backend
```

## 📝 Mô tả các file

### 1. `v2box_connect.php`
- **Chức năng**: File PHP chính xử lý logic backend
- **Nội dung**:
  - Kiểm tra session người dùng
  - Lấy thông tin VLESS config từ database
  - Tạo VLESS URI
  - Tạo QR Code
  - Render HTML

### 2. `css/v2box-connect.css`
- **Chức năng**: File CSS chứa toàn bộ style cho trang
- **Nội dung**:
  - Style cho container, buttons, icons
  - Animation (spinner, hover effects)
  - Responsive design cho mobile
  - Status messages styling

### 3. `js/v2box-connect.js`
- **Chức năng**: File JavaScript xử lý logic phía client
- **Nội dung**:
  - Phát hiện thiết bị (iOS/Android)
  - Mở ứng dụng V2Box với deep link
  - Xử lý fallback khi chưa cài app
  - Copy VLESS URI vào clipboard
  - Hiển thị status messages

## 🔄 Luồng hoạt động

1. User truy cập `v2box_connect.php?id=X`
2. PHP xác thực user và lấy thông tin config
3. PHP tạo VLESS URI và QR Code
4. HTML được render với link đến CSS và JS
5. JavaScript khởi tạo config từ PHP
6. User click "Thêm Cấu Hình"
7. JavaScript phát hiện thiết bị và mở V2Box
8. Nếu chưa cài → chuyển đến App Store/Play Store

## ⚙️ Logic giữ nguyên

✅ Toàn bộ logic PHP được giữ nguyên 100%
✅ Toàn bộ logic JavaScript được giữ nguyên 100%
✅ Chỉ tách riêng CSS và JS ra file độc lập
✅ Giao diện và chức năng hoàn toàn giống như ban đầu

## 🚀 Sử dụng

Chỉ cần upload 3 file/thư mục này lên server và truy cập:
```
https://yourdomain.com/v2box_connect.php?id=YOUR_CONFIG_ID
```

## 📌 Lưu ý

- Đảm bảo thư mục `css/` và `js/` có quyền đọc
- File CSS và JS được link tương đối từ file PHP
- Cần có thư mục `qrcodes/` để lưu QR Code
- Cần có file `db.php` để kết nối database
- Cần thư viện `phpqrcode` để tạo QR Code
