# Hệ Thống Tự Động Tạo Cấu Hình VPN

Hệ thống tự động kết nối với x-ui và 3x-ui panels để tạo cấu hình VPN/Proxy cho khách hàng khi họ đăng ký dịch vụ.

## Tính Năng

- ✅ Kết nối tự động với x-ui và 3x-ui panels
- ✅ API RESTful để nhận đăng ký từ khách hàng
- ✅ Tự động tạo cấu hình theo gói dịch vụ (basic, premium, enterprise)
- ✅ Quản lý nhiều server/panel
- ✅ Theo dõi usage và traffic của khách hàng
- ✅ Gia hạn và xóa cấu hình tự động
- ✅ Load balancing giữa các server
- ✅ API key authentication

## Yêu Cầu

- Python 3.8+
- x-ui hoặc 3x-ui panel đã cài đặt và đang chạy
- Quyền admin để truy cập panel API

## Cài Đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình

Tạo file `config.json` từ `config.example.json`:

```bash
cp config.example.json config.json
```

Chỉnh sửa `config.json` với thông tin panel của bạn:

```json
{
  "threexui_panels": {
    "server1": {
      "url": "https://your-server.com:2053",
      "username": "admin",
      "password": "your_password",
      "default_inbound_id": 1
    }
  },
  "plans": {
    "basic": {
      "panel_type": "3x-ui",
      "data_limit_gb": 50,
      "duration_days": 30,
      "protocol": "vmess",
      "network": "tcp",
      "security": "none",
      "limit_ip": 2
    }
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "api_key": "your_secret_api_key_here"
  }
}
```

### 4. Chạy API Server

```bash
python api_server.py
```

Server sẽ chạy tại `http://localhost:8000`

## Sử Dụng

### API Documentation

Truy cập `http://localhost:8000/docs` để xem tài liệu API đầy đủ (Swagger UI).

### 1. Đăng Ký Khách Hàng Mới

```bash
curl -X POST "http://localhost:8000/api/v1/customer/register" \
  -H "X-API-Key: your_secret_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "name": "Nguyễn Văn A",
    "plan": "premium",
    "phone": "0123456789"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Đã tạo cấu hình VPN thành công",
  "data": {
    "success": true,
    "panel_type": "3x-ui",
    "panel_name": "server1",
    "customer_email": "customer@example.com",
    "config": {
      "success": true,
      "client_data": {...},
      "expiry_time": 1735565229000,
      "total_gb": 200
    },
    "created_at": "2024-11-29T10:30:00"
  }
}
```

### 2. Kiểm Tra Usage Của Khách Hàng

```bash
curl -X POST "http://localhost:8000/api/v1/customer/usage" \
  -H "X-API-Key: your_secret_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com"
  }'
```

### 3. Gia Hạn Dịch Vụ

```bash
curl -X POST "http://localhost:8000/api/v1/customer/renew" \
  -H "X-API-Key: your_secret_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "panel_name": "server1",
    "days": 30
  }'
```

### 4. Xóa Khách Hàng

```bash
curl -X DELETE "http://localhost:8000/api/v1/customer/delete" \
  -H "X-API-Key: your_secret_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "panel_name": "server1",
    "inbound_id": 1
  }'
```

### 5. Xem Danh Sách Gói Dịch Vụ

```bash
curl -X GET "http://localhost:8000/api/v1/plans" \
  -H "X-API-Key: your_secret_api_key_here"
```

## Tích Hợp Với Website

### PHP Example

```php
<?php
function registerCustomer($email, $name, $plan) {
    $url = 'http://your-api-server:8000/api/v1/customer/register';
    $data = [
        'email' => $email,
        'name' => $name,
        'plan' => $plan
    ];
    
    $options = [
        'http' => [
            'header'  => [
                "Content-Type: application/json",
                "X-API-Key: your_secret_api_key_here"
            ],
            'method'  => 'POST',
            'content' => json_encode($data)
        ]
    ];
    
    $context  = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    
    return json_decode($result, true);
}

// Sử dụng khi khách hàng thanh toán thành công
$response = registerCustomer(
    'customer@example.com',
    'Nguyễn Văn A',
    'premium'
);

if ($response['success']) {
    echo "Đã tạo VPN thành công!";
    // Gửi email thông báo cho khách hàng
}
?>
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

async function registerCustomer(email, name, plan) {
  try {
    const response = await axios.post(
      'http://your-api-server:8000/api/v1/customer/register',
      {
        email: email,
        name: name,
        plan: plan
      },
      {
        headers: {
          'X-API-Key': 'your_secret_api_key_here',
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Sử dụng
registerCustomer('customer@example.com', 'Nguyễn Văn A', 'premium')
  .then(result => {
    console.log('Success:', result);
  })
  .catch(error => {
    console.error('Failed:', error);
  });
```

### Python Example

```python
import requests

def register_customer(email, name, plan):
    url = 'http://your-api-server:8000/api/v1/customer/register'
    headers = {
        'X-API-Key': 'your_secret_api_key_here',
        'Content-Type': 'application/json'
    }
    data = {
        'email': email,
        'name': name,
        'plan': plan
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Sử dụng
result = register_customer('customer@example.com', 'Nguyễn Văn A', 'premium')
if result['success']:
    print("Đã tạo VPN thành công!")
```

## Cấu Trúc Dự Án

```
.
├── xui_client.py           # Client API cho x-ui và 3x-ui
├── vpn_service.py          # Service layer quản lý logic
├── api_server.py           # FastAPI server
├── config.json             # File cấu hình (tạo từ example)
├── config.example.json     # Template cấu hình
├── requirements.txt        # Python dependencies
├── examples/               # Các ví dụ tích hợp
│   ├── php_integration.php
│   ├── nodejs_integration.js
│   └── python_integration.py
└── README.md              # Tài liệu này
```

## Các Gói Dịch Vụ Mặc Định

### Basic Plan
- Data: 50GB/tháng
- Thời gian: 30 ngày
- Giới hạn IP: 2 thiết bị
- Protocol: VMess/TCP

### Premium Plan
- Data: 200GB/tháng
- Thời gian: 30 ngày
- Giới hạn IP: 5 thiết bị
- Protocol: VMess/WebSocket + TLS

### Enterprise Plan
- Data: 500GB/tháng
- Thời gian: 30 ngày
- Không giới hạn IP
- Protocol: VLESS/gRPC + TLS

## Bảo Mật

- **API Key**: Luôn sử dụng API key mạnh và giữ bí mật
- **HTTPS**: Khuyến nghị chạy API server sau reverse proxy với SSL/TLS
- **Firewall**: Chỉ cho phép truy cập API từ các IP tin cậy
- **Panel Access**: Bảo vệ quyền admin của x-ui/3x-ui panels

## Troubleshooting

### Không kết nối được với panel

```bash
# Kiểm tra panel có đang chạy không
curl -k https://your-server:2053

# Kiểm tra username/password có đúng không
# Xem log trong terminal khi chạy api_server.py
```

### Lỗi khi tạo client

- Kiểm tra `default_inbound_id` có tồn tại trong panel không
- Đảm bảo port của inbound không bị trùng
- Xem log chi tiết trong terminal

### API không hoạt động

```bash
# Kiểm tra API server đang chạy
curl http://localhost:8000/health

# Kiểm tra API key có đúng không
curl -H "X-API-Key: your_key" http://localhost:8000/api/v1/plans
```

## Deploy Production

### Sử dụng systemd

Tạo file `/etc/systemd/system/vpn-api.service`:

```ini
[Unit]
Description=VPN Auto-Provisioning API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Kích hoạt:
```bash
sudo systemctl enable vpn-api
sudo systemctl start vpn-api
sudo systemctl status vpn-api
```

### Sử dụng Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api_server.py"]
```

Build và chạy:
```bash
docker build -t vpn-api .
docker run -d -p 8000:8000 -v $(pwd)/config.json:/app/config.json vpn-api
```

## Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log của API server
2. Kiểm tra log của x-ui/3x-ui panel
3. Xem phần Troubleshooting ở trên

## License

MIT License
