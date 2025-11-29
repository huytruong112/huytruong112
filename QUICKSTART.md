# Quick Start Guide

Hướng dẫn nhanh để bắt đầu sử dụng hệ thống quản lý VPN.

## Bước 1: Cài đặt

```bash
# Clone repository
git clone <repository-url>
cd <repository-directory>

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt
```

## Bước 2: Cấu hình

```bash
# Copy file cấu hình mẫu
cp .env.example .env

# Chỉnh sửa file .env với thông tin của bạn
nano .env
```

**Quan trọng**: Cần cấu hình ít nhất một trong hai panel (x-ui hoặc 3x-ui):

```env
# X-UI Panel
XUI_PANEL_URL=http://your-server-ip:54321
XUI_USERNAME=admin
XUI_PASSWORD=your-password

# Hoặc 3X-UI Panel
THREEXUI_PANEL_URL=http://your-server-ip:2053
THREEXUI_USERNAME=admin
THREEXUI_PASSWORD=your-password
```

## Bước 3: Chạy ứng dụng

```bash
python main.py
```

API sẽ chạy tại: http://localhost:8000

## Bước 4: Kiểm tra

Mở trình duyệt và truy cập:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Bước 5: Tạo đăng ký đầu tiên

### Cách 1: Sử dụng Swagger UI

1. Truy cập http://localhost:8000/docs
2. Tìm endpoint `POST /subscriptions`
3. Click "Try it out"
4. Điền thông tin:

```json
{
  "customer_email": "customer@example.com",
  "customer_name": "Nguyen Van A",
  "customer_phone": "+84901234567",
  "panel_type": "xui",
  "inbound_id": 1,
  "traffic_limit_gb": 100,
  "expiry_days": 30,
  "protocol": "vless"
}
```

5. Click "Execute"

### Cách 2: Sử dụng curl

```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "customer_name": "Nguyen Van A",
    "panel_type": "xui",
    "inbound_id": 1,
    "traffic_limit_gb": 100,
    "expiry_days": 30
  }'
```

### Cách 3: Sử dụng Python script

```bash
cd examples
python create_subscription_example.py
```

## Bước 6: Lấy cấu hình

Sau khi tạo đăng ký thành công, bạn sẽ nhận được `subscription_id`. Sử dụng ID này để lấy cấu hình:

```bash
curl "http://localhost:8000/subscriptions/1/config"
```

## Các thao tác phổ biến

### Xem tất cả endpoints

```bash
curl http://localhost:8000/docs
```

### Gia hạn đăng ký

```bash
curl -X POST "http://localhost:8000/subscriptions/1/renew" \
  -H "Content-Type: application/json" \
  -d '{
    "additional_days": 30,
    "additional_traffic_gb": 50
  }'
```

### Tạm ngưng đăng ký

```bash
curl -X PUT "http://localhost:8000/subscriptions/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "suspended",
    "enable": false
  }'
```

### Kích hoạt lại

```bash
curl -X PUT "http://localhost:8000/subscriptions/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active",
    "enable": true
  }'
```

### Đồng bộ lưu lượng

```bash
curl -X POST "http://localhost:8000/subscriptions/1/sync-traffic"
```

## Lưu ý quan trọng

### 1. Lấy Inbound ID

Trước khi tạo đăng ký, bạn cần biết `inbound_id` từ panel của bạn:

1. Đăng nhập vào x-ui hoặc 3x-ui panel
2. Vào phần "Inbounds"
3. Xem ID của inbound bạn muốn sử dụng (thường là 1, 2, 3...)

### 2. Panel Type

- Sử dụng `"xui"` cho x-ui panel (dopaemon/x-ui)
- Sử dụng `"3x-ui"` cho 3x-ui panel (mhsanaei/3x-ui)

### 3. Traffic Limit

- `traffic_limit_gb: 0` = unlimited (không giới hạn)
- `traffic_limit_gb: 50` = 50GB
- `traffic_limit_gb: 100` = 100GB

## Triển khai Production

### Sử dụng Docker

```bash
# Build và chạy
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng
docker-compose down
```

### Sử dụng systemd

1. Tạo file service:

```bash
sudo nano /etc/systemd/system/vpn-api.service
```

2. Thêm nội dung:

```ini
[Unit]
Description=VPN Subscription API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable và start:

```bash
sudo systemctl enable vpn-api
sudo systemctl start vpn-api
sudo systemctl status vpn-api
```

### Sử dụng nginx

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Lỗi: Cannot connect to panel

**Giải pháp**:
1. Kiểm tra panel URL trong `.env`
2. Đảm bảo panel đang chạy
3. Kiểm tra firewall
4. Test kết nối: `curl http://your-panel-url/login`

### Lỗi: Authentication failed

**Giải pháp**:
1. Kiểm tra username/password trong `.env`
2. Đăng nhập thử vào panel qua trình duyệt
3. Đảm bảo user có quyền quản trị

### Lỗi: Inbound not found

**Giải pháp**:
1. Kiểm tra `inbound_id` có đúng không
2. Vào panel xem danh sách inbounds
3. Sử dụng ID đúng từ panel

### Database locked

**Giải pháp**:
```bash
rm vpn_service.db
python main.py
```

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs
2. Xem API documentation tại `/docs`
3. Tạo issue trên GitHub
