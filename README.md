# VPN Service Auto Provisioning System

Hệ thống tự động tạo cấu hình VPN khi khách hàng đăng ký dịch vụ, tích hợp với x-ui và 3x-ui panels.

## Tính năng chính

✅ **Tự động tạo cấu hình VPN** - Khi khách hàng đăng ký, hệ thống tự động:
- Tạo tài khoản khách hàng
- Chọn panel x-ui/3x-ui phù hợp
- Tạo client VPN trên panel
- Trả về thông tin kết nối ngay lập tức

✅ **Hỗ trợ nhiều panel** - Có thể kết nối với nhiều panel x-ui hoặc 3x-ui cùng lúc

✅ **Quản lý khách hàng** - 
- Đăng ký/đăng nhập
- Xem thông tin cấu hình VPN
- Gia hạn dịch vụ
- Theo dõi dung lượng sử dụng

✅ **RESTful API** - Dễ dàng tích hợp với website, app di động

## Cấu trúc dự án

```
.
├── main.py              # FastAPI application - API endpoints
├── config.py            # Configuration settings
├── database.py          # Database models (SQLAlchemy)
├── auth.py              # Authentication utilities
├── schemas.py           # Pydantic schemas
├── service.py           # Business logic layer
├── xui_client.py        # X-UI panel API client
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # Documentation
```

## Yêu cầu hệ thống

- Python 3.8+
- x-ui hoặc 3x-ui panel đã cài đặt và chạy
- SQLite (hoặc PostgreSQL cho production)

## Cài đặt

### 1. Clone repository

```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Tạo môi trường ảo và cài đặt dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Cấu hình môi trường

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
# Database
DATABASE_URL=sqlite:///./vpn_service.db

# Security - ĐỔI SECRET_KEY!
SECRET_KEY=your-super-secret-key-change-this

# X-UI Panel 1 (dopaemon/x-ui)
XUI_1_URL=http://your-server-ip:54321
XUI_1_USERNAME=admin
XUI_1_PASSWORD=admin_password
XUI_1_ENABLED=true

# 3X-UI Panel (mhsanaei/3x-ui)
XUI_2_URL=http://your-server-ip:2053
XUI_2_USERNAME=admin
XUI_2_PASSWORD=admin_password
XUI_2_ENABLED=true

# Service Settings
DEFAULT_TRAFFIC_LIMIT_GB=50
DEFAULT_EXPIRY_DAYS=30
```

### 4. Khởi chạy ứng dụng

```bash
python main.py
```

Hoặc sử dụng uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API sẽ chạy tại: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Sử dụng API

### 1. Đăng ký khách hàng mới (Tự động tạo VPN)

**Endpoint:** `POST /register`

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "username": "customer1",
    "password": "secure_password",
    "full_name": "Nguyễn Văn A",
    "phone": "0123456789",
    "traffic_limit_gb": 50,
    "service_duration_days": 30
  }'
```

**Response:**

```json
{
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "username": "customer1",
    "full_name": "Nguyễn Văn A",
    "phone": "0123456789",
    "is_active": true,
    "created_at": "2025-11-29T10:30:00"
  },
  "vpn_config": {
    "id": 1,
    "config_name": "customer1-xui_1",
    "protocol": "vless",
    "panel_type": "xui_1",
    "service_status": "active",
    "traffic_limit_gb": 50,
    "traffic_used_gb": 0,
    "activated_at": "2025-11-29T10:30:00",
    "expires_at": "2025-12-29T10:30:00",
    "connection_url": "vless://uuid@server:port?type=tcp&security=none#customer1",
    "created_at": "2025-11-29T10:30:00"
  },
  "message": "Service registered successfully! Please save your connection details."
}
```

### 2. Đăng nhập

**Endpoint:** `POST /login`

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer1",
    "password": "secure_password"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Xem thông tin cấu hình VPN của tôi

**Endpoint:** `GET /my-vpn-configs`

```bash
curl -X GET "http://localhost:8000/my-vpn-configs" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Xem thống kê sử dụng

**Endpoint:** `GET /vpn-config/{config_id}/stats`

```bash
curl -X GET "http://localhost:8000/vpn-config/1/stats" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Gia hạn dịch vụ

**Endpoint:** `POST /vpn-config/{config_id}/renew`

```bash
curl -X POST "http://localhost:8000/vpn-config/1/renew?additional_days=30&additional_traffic_gb=50" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Kiểm tra panel khả dụng

**Endpoint:** `GET /panels`

```bash
curl -X GET "http://localhost:8000/panels"
```

## Tích hợp với website

### Ví dụ JavaScript/HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>Đăng ký dịch vụ VPN</title>
</head>
<body>
    <h1>Đăng ký dịch vụ VPN</h1>
    
    <form id="registerForm">
        <input type="email" id="email" placeholder="Email" required><br>
        <input type="text" id="username" placeholder="Username" required><br>
        <input type="password" id="password" placeholder="Password" required><br>
        <input type="text" id="full_name" placeholder="Họ tên"><br>
        <input type="tel" id="phone" placeholder="Số điện thoại"><br>
        
        <label>Dung lượng (GB):</label>
        <select id="traffic_limit_gb">
            <option value="30">30 GB</option>
            <option value="50" selected>50 GB</option>
            <option value="100">100 GB</option>
        </select><br>
        
        <label>Thời hạn (ngày):</label>
        <select id="service_duration_days">
            <option value="30" selected>30 ngày</option>
            <option value="60">60 ngày</option>
            <option value="90">90 ngày</option>
        </select><br>
        
        <button type="submit">Đăng ký ngay</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                email: document.getElementById('email').value,
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                full_name: document.getElementById('full_name').value,
                phone: document.getElementById('phone').value,
                traffic_limit_gb: parseInt(document.getElementById('traffic_limit_gb').value),
                service_duration_days: parseInt(document.getElementById('service_duration_days').value)
            };
            
            try {
                const response = await fetch('http://localhost:8000/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    document.getElementById('result').innerHTML = `
                        <h2>Đăng ký thành công!</h2>
                        <p><strong>Username:</strong> ${result.customer.username}</p>
                        <p><strong>Email:</strong> ${result.customer.email}</p>
                        <h3>Thông tin kết nối VPN:</h3>
                        <p><strong>Connection URL:</strong></p>
                        <textarea rows="3" cols="80">${result.vpn_config.connection_url}</textarea>
                        <p><strong>Dung lượng:</strong> ${result.vpn_config.traffic_limit_gb} GB</p>
                        <p><strong>Hết hạn:</strong> ${result.vpn_config.expires_at}</p>
                    `;
                } else {
                    document.getElementById('result').innerHTML = `
                        <p style="color: red;">Lỗi: ${result.detail}</p>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <p style="color: red;">Lỗi kết nối: ${error.message}</p>
                `;
            }
        });
    </script>
</body>
</html>
```

## Triển khai Production

### Sử dụng Docker (Khuyến nghị)

Tạo file `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Tạo file `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/vpn_service
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=vpn_service
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

Chạy:

```bash
docker-compose up -d
```

### Sử dụng Nginx làm reverse proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Bảo mật

1. **Đổi SECRET_KEY** trong file `.env`
2. **Sử dụng HTTPS** cho production
3. **Bảo mật thông tin panel** - không để lộ username/password
4. **Giới hạn rate limiting** để tránh abuse
5. **Backup database** thường xuyên

## Khắc phục sự cố

### Panel không kết nối được

1. Kiểm tra URL panel có đúng không
2. Kiểm tra username/password
3. Kiểm tra firewall cho phép kết nối
4. Kiểm tra panel có đang chạy không

### Database error

```bash
# Xóa database cũ và tạo mới
rm vpn_service.db
python main.py
```

### Connection URL không đúng

- Kiểm tra cấu hình inbound trên panel
- Xem log để debug: `uvicorn main:app --log-level debug`

## API Documentation

Sau khi chạy ứng dụng, truy cập:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs
2. Xem API documentation
3. Tạo issue trên GitHub

## License

MIT License

## Tác giả

Created with ❤️ for automated VPN service provisioning
