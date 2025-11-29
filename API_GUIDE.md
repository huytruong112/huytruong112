# API Usage Guide

Hướng dẫn chi tiết sử dụng API.

## Base URL

```
http://localhost:8000
```

## Authentication

Hiện tại API chưa có authentication. Trong production, bạn nên thêm:
- API Key authentication
- JWT tokens
- OAuth2

## Endpoints

### 1. Health Check

Kiểm tra trạng thái API và panel được cấu hình.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "panels": {
    "x-ui_configured": true,
    "3x-ui_configured": false
  }
}
```

---

### 2. Create Customer

Tạo khách hàng mới.

**Request:**
```http
POST /customers
Content-Type: application/json

{
  "email": "customer@example.com",
  "name": "Nguyen Van A",
  "phone": "+84901234567"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "customer@example.com",
  "name": "Nguyen Van A",
  "phone": "+84901234567",
  "created_at": "2025-11-29T10:00:00"
}
```

---

### 3. Create Subscription

Tạo đăng ký VPN mới cho khách hàng. Endpoint này sẽ:
1. Tạo khách hàng nếu chưa tồn tại
2. Tạo client trong panel (x-ui hoặc 3x-ui)
3. Lưu thông tin đăng ký vào database

**Request:**
```http
POST /subscriptions
Content-Type: application/json

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

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_email | string | Yes | Email khách hàng |
| customer_name | string | Yes | Tên khách hàng |
| customer_phone | string | No | Số điện thoại |
| panel_type | string | Yes | "xui" hoặc "3x-ui" |
| inbound_id | integer | Yes | ID của inbound trong panel |
| traffic_limit_gb | float | No | Giới hạn lưu lượng (0 = unlimited) |
| expiry_days | integer | No | Số ngày hết hạn (default: 30) |
| protocol | string | No | Protocol (default: "vless") |

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "panel_type": "xui",
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "email_identifier": "customer@example.com_550e8400",
  "protocol": "vless",
  "traffic_limit_gb": 100,
  "traffic_used_gb": 0,
  "expiry_date": "2025-12-29T10:00:00",
  "status": "active",
  "is_enabled": true,
  "created_at": "2025-11-29T10:00:00"
}
```

**Example with curl:**
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

---

### 4. Get Subscription

Lấy thông tin chi tiết đăng ký.

**Request:**
```http
GET /subscriptions/{subscription_id}
```

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "panel_type": "xui",
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "email_identifier": "customer@example.com_550e8400",
  "protocol": "vless",
  "traffic_limit_gb": 100,
  "traffic_used_gb": 15.5,
  "expiry_date": "2025-12-29T10:00:00",
  "status": "active",
  "is_enabled": true,
  "created_at": "2025-11-29T10:00:00"
}
```

---

### 5. Get Configuration

Lấy cấu hình kết nối cho đăng ký.

**Request:**
```http
GET /subscriptions/{subscription_id}/config
```

**Response:**
```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "email": "customer@example.com_550e8400",
  "protocol": "vless",
  "address": "your-server.com",
  "port": 443,
  "network": "tcp",
  "security": "tls",
  "expiry_date": "2025-12-29T10:00:00",
  "traffic_limit_gb": 100,
  "traffic_used_gb": 15.5,
  "status": "active"
}
```

---

### 6. Generate QR Code

Tạo và lấy QR code cho đăng ký.

**Request:**
```http
GET /subscriptions/{subscription_id}/qrcode?connection_url={url}
```

**Parameters:**
- `connection_url`: URL kết nối (vless://, vmess://, trojan://, etc.)

**Response:**
- Content-Type: `image/png`
- Binary PNG image data

**Example:**
```bash
curl "http://localhost:8000/subscriptions/1/qrcode?connection_url=vless://550e8400@server.com:443" \
  --output qrcode.png
```

---

### 7. Update Subscription

Cập nhật trạng thái đăng ký.

**Request:**
```http
PUT /subscriptions/{subscription_id}
Content-Type: application/json

{
  "status": "suspended",
  "enable": false
}
```

**Status values:**
- `active`: Đang hoạt động
- `suspended`: Tạm ngưng
- `expired`: Hết hạn
- `cancelled`: Đã hủy

**Response:**
```json
{
  "id": 1,
  "status": "suspended",
  "is_enabled": false,
  ...
}
```

---

### 8. Renew Subscription

Gia hạn đăng ký.

**Request:**
```http
POST /subscriptions/{subscription_id}/renew
Content-Type: application/json

{
  "additional_days": 30,
  "additional_traffic_gb": 50
}
```

**Parameters:**
- `additional_days`: Số ngày muốn gia hạn thêm
- `additional_traffic_gb`: Lưu lượng muốn thêm (GB)

**Response:**
```json
{
  "id": 1,
  "expiry_date": "2026-01-29T10:00:00",
  "traffic_limit_gb": 150,
  "status": "active",
  ...
}
```

---

### 9. Delete Subscription

Xóa đăng ký (cả trong database và panel).

**Request:**
```http
DELETE /subscriptions/{subscription_id}
```

**Response:**
- Status Code: 204 No Content

---

### 10. Sync Traffic

Đồng bộ lưu lượng sử dụng từ panel.

**Request:**
```http
POST /subscriptions/{subscription_id}/sync-traffic
```

**Response:**
```json
{
  "message": "Traffic synced successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Subscription not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to create subscription in panel"
}
```

---

## Integration Examples

### Python

```python
import httpx
import asyncio

async def create_subscription():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/subscriptions",
            json={
                "customer_email": "customer@example.com",
                "customer_name": "Nguyen Van A",
                "panel_type": "xui",
                "inbound_id": 1,
                "traffic_limit_gb": 100,
                "expiry_days": 30
            }
        )
        
        if response.status_code == 201:
            subscription = response.json()
            print(f"Created subscription: {subscription['id']}")
            return subscription
        else:
            print(f"Error: {response.text}")
            return None

asyncio.run(create_subscription())
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function createSubscription() {
  try {
    const response = await axios.post('http://localhost:8000/subscriptions', {
      customer_email: 'customer@example.com',
      customer_name: 'Nguyen Van A',
      panel_type: 'xui',
      inbound_id: 1,
      traffic_limit_gb: 100,
      expiry_days: 30
    });
    
    console.log('Created subscription:', response.data.id);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    return null;
  }
}

createSubscription();
```

### PHP

```php
<?php

function createSubscription() {
    $data = [
        'customer_email' => 'customer@example.com',
        'customer_name' => 'Nguyen Van A',
        'panel_type' => 'xui',
        'inbound_id' => 1,
        'traffic_limit_gb' => 100,
        'expiry_days' => 30
    ];
    
    $ch = curl_init('http://localhost:8000/subscriptions');
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 201) {
        $subscription = json_decode($response, true);
        echo "Created subscription: " . $subscription['id'] . "\n";
        return $subscription;
    } else {
        echo "Error: $response\n";
        return null;
    }
}

createSubscription();
```

---

## Rate Limiting

Khuyến nghị thêm rate limiting trong production:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/subscriptions")
@limiter.limit("10/minute")
async def create_subscription(...):
    ...
```

---

## Best Practices

1. **Error Handling**: Luôn kiểm tra status code và xử lý lỗi
2. **Retry Logic**: Implement retry cho các request quan trọng
3. **Timeout**: Set timeout hợp lý cho requests
4. **Logging**: Log tất cả các request quan trọng
5. **Validation**: Validate input trước khi gửi request
6. **Security**: Sử dụng HTTPS trong production
7. **Monitoring**: Monitor API health và performance

---

## Testing

### Manual Testing với curl

```bash
# Test health
curl http://localhost:8000/health

# Create subscription
curl -X POST http://localhost:8000/subscriptions \
  -H "Content-Type: application/json" \
  -d @test_data.json

# Get config
curl http://localhost:8000/subscriptions/1/config

# Renew
curl -X POST http://localhost:8000/subscriptions/1/renew \
  -H "Content-Type: application/json" \
  -d '{"additional_days": 30}'
```

### Automated Testing

```python
import pytest
import httpx

@pytest.mark.asyncio
async def test_create_subscription():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/subscriptions",
            json={
                "customer_email": "test@example.com",
                "customer_name": "Test User",
                "panel_type": "xui",
                "inbound_id": 1
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "active"
```
