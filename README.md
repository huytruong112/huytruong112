# VPN Subscription Management System

Hệ thống quản lý tự động đăng ký VPN với x-ui và 3x-ui panels. Tự động tạo cấu hình khi khách hàng đăng ký dịch vụ.

## Tính năng

- ✅ Tích hợp với x-ui panel (dopaemon/x-ui)
- ✅ Tích hợp với 3x-ui panel (mhsanaei/3x-ui)
- ✅ Tự động tạo cấu hình VPN khi khách hàng đăng ký
- ✅ Quản lý khách hàng và đăng ký
- ✅ Theo dõi lưu lượng sử dụng
- ✅ Gia hạn và cập nhật đăng ký
- ✅ Tạo QR code cho cấu hình
- ✅ RESTful API với FastAPI
- ✅ Quản lý trạng thái đăng ký (active, expired, suspended, cancelled)

## Yêu cầu hệ thống

- Python 3.8+
- x-ui hoặc 3x-ui panel đã cài đặt và cấu hình

## Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./vpn_service.db

# X-UI Panel Configuration
XUI_PANEL_URL=http://your-xui-panel.com:54321
XUI_USERNAME=admin
XUI_PASSWORD=admin

# 3X-UI Panel Configuration
THREEXUI_PANEL_URL=http://your-3xui-panel.com:2053
THREEXUI_USERNAME=admin
THREEXUI_PASSWORD=admin

# Service Configuration
DEFAULT_TRAFFIC_LIMIT_GB=50
DEFAULT_EXPIRY_DAYS=30
DEFAULT_PROTOCOL=vless
```

### 5. Chạy ứng dụng

```bash
python main.py
```

API sẽ chạy tại `http://localhost:8000`

## API Documentation

Sau khi chạy ứng dụng, bạn có thể truy cập:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Sử dụng

### 1. Tạo đăng ký mới cho khách hàng

```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "customer_name": "Nguyen Van A",
    "customer_phone": "+84901234567",
    "panel_type": "xui",
    "inbound_id": 1,
    "traffic_limit_gb": 100,
    "expiry_days": 30,
    "protocol": "vless"
  }'
```

Hoặc với 3x-ui:

```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "customer_name": "Nguyen Van A",
    "customer_phone": "+84901234567",
    "panel_type": "3x-ui",
    "inbound_id": 1,
    "traffic_limit_gb": 100,
    "expiry_days": 30,
    "protocol": "vless"
  }'
```

### 2. Lấy thông tin cấu hình

```bash
curl "http://localhost:8000/subscriptions/1/config"
```

### 3. Tạo QR code

```bash
curl "http://localhost:8000/subscriptions/1/qrcode?connection_url=vless://..." \
  --output qrcode.png
```

### 4. Gia hạn đăng ký

```bash
curl -X POST "http://localhost:8000/subscriptions/1/renew" \
  -H "Content-Type: application/json" \
  -d '{
    "additional_days": 30,
    "additional_traffic_gb": 50
  }'
```

### 5. Cập nhật trạng thái

```bash
curl -X PUT "http://localhost:8000/subscriptions/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "suspended",
    "enable": false
  }'
```

### 6. Đồng bộ lưu lượng

```bash
curl -X POST "http://localhost:8000/subscriptions/1/sync-traffic"
```

### 7. Xóa đăng ký

```bash
curl -X DELETE "http://localhost:8000/subscriptions/1"
```

## Tích hợp với hệ thống thanh toán

Bạn có thể tích hợp API này với:

- Website đăng ký dịch vụ
- Cổng thanh toán (payment gateway)
- Telegram bot
- Discord bot
- Hệ thống CRM

### Ví dụ: Tích hợp với website

```javascript
// Frontend - Khi khách hàng hoàn tất thanh toán
async function createSubscription(customerData, planData) {
  const response = await fetch('http://your-api.com/subscriptions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      customer_email: customerData.email,
      customer_name: customerData.name,
      customer_phone: customerData.phone,
      panel_type: 'xui', // hoặc '3x-ui'
      inbound_id: planData.inboundId,
      traffic_limit_gb: planData.trafficLimit,
      expiry_days: planData.duration,
      protocol: 'vless'
    })
  });
  
  const subscription = await response.json();
  
  // Lấy cấu hình
  const config = await fetch(`http://your-api.com/subscriptions/${subscription.id}/config`)
    .then(r => r.json());
  
  // Hiển thị cho khách hàng
  displayConfig(config);
}
```

### Ví dụ: Webhook sau thanh toán

```python
from fastapi import FastAPI, Request
import httpx

webhook_app = FastAPI()

@webhook_app.post("/payment-webhook")
async def payment_webhook(request: Request):
    """Webhook nhận thông báo từ payment gateway"""
    data = await request.json()
    
    if data['status'] == 'paid':
        # Tạo subscription tự động
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'http://localhost:8000/subscriptions',
                json={
                    'customer_email': data['customer_email'],
                    'customer_name': data['customer_name'],
                    'customer_phone': data['customer_phone'],
                    'panel_type': 'xui',
                    'inbound_id': 1,
                    'traffic_limit_gb': data['plan_traffic'],
                    'expiry_days': data['plan_days'],
                    'protocol': 'vless'
                }
            )
            
            if response.status_code == 201:
                subscription = response.json()
                
                # Gửi email cho khách hàng với thông tin cấu hình
                await send_welcome_email(
                    data['customer_email'],
                    subscription['id']
                )
                
    return {'status': 'success'}
```

## Cấu trúc dự án

```
.
├── clients/                  # API clients cho các panel
│   ├── __init__.py
│   ├── xui_client.py        # Client cho x-ui
│   └── threexui_client.py   # Client cho 3x-ui
├── services/                 # Business logic
│   ├── __init__.py
│   └── vpn_service.py       # Service quản lý VPN
├── models.py                # Database models
├── database.py              # Database configuration
├── schemas.py               # Pydantic schemas
├── config.py                # Application configuration
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## API Endpoints

### Customers

- `POST /customers` - Tạo khách hàng mới

### Subscriptions

- `POST /subscriptions` - Tạo đăng ký mới (tự động tạo trong panel)
- `GET /subscriptions/{id}` - Lấy thông tin đăng ký
- `GET /subscriptions/{id}/config` - Lấy cấu hình kết nối
- `GET /subscriptions/{id}/qrcode` - Tạo và lấy QR code
- `PUT /subscriptions/{id}` - Cập nhật trạng thái
- `POST /subscriptions/{id}/renew` - Gia hạn đăng ký
- `DELETE /subscriptions/{id}` - Xóa đăng ký
- `POST /subscriptions/{id}/sync-traffic` - Đồng bộ lưu lượng

### Health

- `GET /health` - Kiểm tra trạng thái hệ thống
- `GET /` - Thông tin API

## Bảo mật

### Khuyến nghị

1. **Thay đổi API_SECRET_KEY**: Đặt một key phức tạp trong `.env`
2. **Sử dụng HTTPS**: Triển khai với reverse proxy (nginx) và SSL
3. **Giới hạn rate**: Thêm rate limiting để tránh abuse
4. **Authentication**: Thêm JWT hoặc API key authentication
5. **Firewall**: Chỉ cho phép truy cập từ IP tin cậy

### Ví dụ với nginx

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Kiểm tra health

```bash
curl http://localhost:8000/health
```

### Xem logs

Logs được ghi ra console. Để lưu vào file:

```bash
python main.py 2>&1 | tee -a app.log
```

Hoặc sử dụng systemd service:

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

## Troubleshooting

### Lỗi kết nối đến panel

- Kiểm tra URL, username, password trong `.env`
- Đảm bảo panel đang chạy và có thể truy cập
- Kiểm tra firewall

### Lỗi tạo client

- Kiểm tra inbound_id có tồn tại không
- Kiểm tra quyền của user trong panel
- Xem logs để biết chi tiết lỗi

### Database errors

- Đảm bảo có quyền ghi vào thư mục
- Xóa file database cũ và chạy lại để tạo mới

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

Nếu bạn gặp vấn đề hoặc có câu hỏi, vui lòng tạo issue trên GitHub.
