# 🚀 Hệ Thống Quản Lý Dịch Vụ 3X-UI

Hệ thống tự động tạo client trong 3X-UI khi khách hàng mua gói dịch vụ VPN.

## ✨ Tính năng

### Khách hàng:
- ✅ Đăng ký/Đăng nhập tài khoản
- ✅ Xem danh sách gói dịch vụ
- ✅ Mua gói dịch vụ và tự động nhận client
- ✅ Quản lý các dịch vụ đã mua
- ✅ Lấy URL kết nối và subscription URL

### Admin:
- ✅ Dashboard thống kê tổng quan
- ✅ Quản lý khách hàng
- ✅ Quản lý đơn hàng
- ✅ Quản lý clients (kích hoạt/vô hiệu hóa/xóa)
- ✅ Quản lý gói dịch vụ (thêm/sửa/xóa)

### Tích hợp 3X-UI:
- ✅ Tự động tạo client khi khách mua gói
- ✅ Đồng bộ thông tin client
- ✅ Quản lý traffic và thời hạn
- ✅ Tạo subscription URL

## 📋 Yêu cầu hệ thống

- Node.js >= 14.x
- 3X-UI Panel đã cài đặt và chạy
- SQLite3

## 🛠️ Cài đặt

### 1. Clone hoặc tải source code

```bash
git clone <repository-url>
cd 3x-ui-service-manager
```

### 2. Cài đặt dependencies

```bash
npm install
```

### 3. Cấu hình

Tạo file `.env` từ file mẫu:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
# Cấu hình 3X-UI Panel
X3UI_PANEL_URL=http://your-server-ip:2053
X3UI_USERNAME=admin
X3UI_PASSWORD=admin

# Cấu hình Server
PORT=3000
JWT_SECRET=your-secret-key-change-this

# Cấu hình Database
DB_PATH=./database.sqlite

# Cấu hình Inbound (ID của inbound trong 3X-UI)
DEFAULT_INBOUND_ID=1
```

**Quan trọng:** 
- Thay `your-server-ip` bằng IP hoặc domain của server 3X-UI
- Thay username/password nếu bạn đã đổi
- Thay `JWT_SECRET` bằng một chuỗi ngẫu nhiên an toàn
- Kiểm tra `DEFAULT_INBOUND_ID` trong 3X-UI panel (thường là 1)

### 4. Khởi động server

```bash
npm start
```

Hoặc chạy ở chế độ development (tự động restart khi có thay đổi):

```bash
npm run dev
```

## 🌐 Truy cập

Sau khi khởi động thành công:

- **Website khách hàng:** http://localhost:3000
- **Admin panel:** http://localhost:3000/admin

## 📖 Hướng dẫn sử dụng

### Cho khách hàng:

1. **Đăng ký tài khoản**
   - Truy cập trang chủ
   - Click tab "Đăng Ký"
   - Điền thông tin và đăng ký

2. **Mua gói dịch vụ**
   - Đăng nhập
   - Chọn gói dịch vụ phù hợp
   - Click "Mua Ngay"
   - Client sẽ được tạo tự động trong 3X-UI

3. **Sử dụng dịch vụ**
   - Vào phần "Dịch Vụ Của Tôi"
   - Copy URL kết nối hoặc subscription URL
   - Import vào ứng dụng VPN client (v2rayN, v2rayNG, etc.)

### Cho Admin:

1. **Truy cập admin panel**
   - Vào http://localhost:3000/admin

2. **Quản lý gói dịch vụ**
   - Vào mục "Gói Dịch Vụ"
   - Thêm/sửa/xóa gói theo nhu cầu

3. **Quản lý clients**
   - Vào mục "Clients"
   - Có thể vô hiệu hóa/kích hoạt lại/xóa client
   - Xem thông tin traffic và thời hạn

4. **Theo dõi đơn hàng và doanh thu**
   - Dashboard hiển thị thống kê tổng quan
   - Mục "Đơn Hàng" để xem chi tiết

## 🔧 Cấu hình nâng cao

### Thay đổi Inbound mặc định

Nếu bạn muốn sử dụng inbound khác trong 3X-UI:

1. Truy cập 3X-UI panel
2. Vào "Inbounds"
3. Copy ID của inbound muốn sử dụng
4. Cập nhật `DEFAULT_INBOUND_ID` trong file `.env`

### Tích hợp thanh toán

Để tích hợp cổng thanh toán tự động (VNPay, Momo, Stripe...):

1. Cài đặt SDK của cổng thanh toán
2. Sửa file `routes/api.js` - endpoint `/api/orders`
3. Thêm logic xử lý webhook từ cổng thanh toán

### Tùy chỉnh giao diện

- Frontend customer: `/public/index.html`
- Frontend admin: `/public/admin.html`
- Bạn có thể tùy chỉnh CSS và HTML theo ý muốn

## 🔐 Bảo mật

**Lưu ý quan trọng:**

1. **Đổi JWT_SECRET:** Sử dụng chuỗi ngẫu nhiên mạnh
2. **HTTPS:** Nên chạy qua HTTPS trong môi trường production
3. **Firewall:** Bảo vệ 3X-UI panel (chỉ cho phép truy cập từ localhost)
4. **Admin Panel:** Nên thêm authentication cho admin panel
5. **Rate Limiting:** Cân nhắc thêm rate limiting để chống spam

## 🐛 Xử lý sự cố

### Lỗi kết nối 3X-UI

```
❌ Lỗi đăng nhập 3X-UI
```

**Giải pháp:**
- Kiểm tra `X3UI_PANEL_URL` đúng chưa
- Kiểm tra username/password
- Đảm bảo 3X-UI đang chạy
- Kiểm tra firewall

### Lỗi không tạo được client

```
❌ Lỗi tạo client trong 3X-UI
```

**Giải pháp:**
- Kiểm tra `DEFAULT_INBOUND_ID` có đúng không
- Đảm bảo inbound đang enable
- Kiểm tra log trong 3X-UI panel

### Database lỗi

**Giải pháp:**
- Xóa file `database.sqlite` và khởi động lại (sẽ mất dữ liệu)
- Hoặc backup database trước khi xóa

## 📁 Cấu trúc thư mục

```
.
├── database/
│   └── init.js              # Khởi tạo database
├── routes/
│   ├── api.js               # API routes cho customer
│   └── admin.js             # API routes cho admin
├── services/
│   └── x3ui.js              # Service tương tác với 3X-UI
├── public/
│   ├── index.html           # Frontend customer
│   └── admin.html           # Frontend admin
├── server.js                # Entry point
├── package.json
├── .env.example
└── README.md
```

## 🔄 API Endpoints

### Customer APIs

- `GET /api/packages` - Lấy danh sách gói dịch vụ
- `POST /api/register` - Đăng ký khách hàng
- `POST /api/login` - Đăng nhập
- `POST /api/orders` - Tạo đơn hàng (yêu cầu auth)
- `GET /api/my-services` - Lấy dịch vụ của tôi (yêu cầu auth)

### Admin APIs

- `GET /admin/api/stats` - Thống kê tổng quan
- `GET /admin/api/customers` - Danh sách khách hàng
- `GET /admin/api/orders` - Danh sách đơn hàng
- `GET /admin/api/clients` - Danh sách clients
- `POST /admin/api/packages` - Tạo gói dịch vụ mới
- `DELETE /admin/api/packages/:id` - Xóa gói dịch vụ
- `POST /admin/api/clients/:id/disable` - Vô hiệu hóa client
- `POST /admin/api/clients/:id/enable` - Kích hoạt client
- `DELETE /admin/api/clients/:id` - Xóa client

## 🚀 Deploy lên production

### Sử dụng PM2

```bash
npm install -g pm2
pm2 start server.js --name 3x-ui-service
pm2 save
pm2 startup
```

### Sử dụng Docker (tùy chọn)

```bash
# Tạo Dockerfile
# Build image
docker build -t 3x-ui-service .

# Run container
docker run -d -p 3000:3000 --env-file .env 3x-ui-service
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📝 License

MIT

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## 📧 Hỗ trợ

Nếu bạn gặp vấn đề, vui lòng:
1. Kiểm tra phần "Xử lý sự cố" ở trên
2. Tạo issue trên GitHub
3. Liên hệ qua email

---

**Chúc bạn sử dụng thành công! 🎉**
