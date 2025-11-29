# API Examples & Usage

Tài liệu chi tiết về cách sử dụng API

## Base URL

```
http://localhost:8000
```

Hoặc với domain của bạn:
```
https://api.yourdomain.com
```

## Endpoints Overview

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | API info |
| `/health` | GET | No | Health check |
| `/register` | POST | No | Register new customer + auto create VPN |
| `/login` | POST | No | Customer login |
| `/panels` | GET | No | List available panels |
| `/me` | GET | Yes | Get current customer info |
| `/my-vpn-configs` | GET | Yes | List my VPN configs |
| `/vpn-config/{id}` | GET | Yes | Get specific VPN config |
| `/vpn-config/{id}/stats` | GET | Yes | Get usage statistics |
| `/vpn-config/{id}/renew` | POST | Yes | Renew service |
| `/vpn-config/{id}/suspend` | POST | Yes | Suspend service |

---

## 1. Register New Customer

**Đây là endpoint quan trọng nhất - tự động tạo VPN khi đăng ký!**

### Request

```bash
POST /register
Content-Type: application/json
```

```json
{
  "email": "customer@example.com",
  "username": "customer1",
  "password": "securepass123",
  "full_name": "Nguyễn Văn A",
  "phone": "0123456789",
  "traffic_limit_gb": 50,
  "service_duration_days": 30,
  "panel_type": null,
  "inbound_id": null
}
```

**Parameters:**

- `email` (required): Email address
- `username` (required): Username (alphanumeric + underscore)
- `password` (required): Password (min 6 characters)
- `full_name` (optional): Full name
- `phone` (optional): Phone number
- `traffic_limit_gb` (optional): Traffic limit in GB (default: 50)
- `service_duration_days` (optional): Service duration in days (default: 30)
- `panel_type` (optional): "xui_1" or "xui_2" (auto-select if null)
- `inbound_id` (optional): Specific inbound ID (auto-select if null)

### Response Success (201)

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
    "subscription_url": null,
    "created_at": "2025-11-29T10:30:00"
  },
  "message": "Service registered successfully! Please save your connection details."
}
```

### Response Error (400)

```json
{
  "detail": "Customer with this email or username already exists"
}
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "traffic_limit_gb": 50,
    "service_duration_days": 30
  }'
```

### Python Example

```python
import requests

url = "http://localhost:8000/register"
data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User",
    "phone": "0123456789",
    "traffic_limit_gb": 50,
    "service_duration_days": 30
}

response = requests.post(url, json=data)

if response.status_code == 201:
    result = response.json()
    print(f"✅ Success!")
    print(f"Username: {result['customer']['username']}")
    print(f"Connection URL: {result['vpn_config']['connection_url']}")
else:
    print(f"❌ Error: {response.json()['detail']}")
```

### JavaScript Example

```javascript
const registerCustomer = async () => {
    const data = {
        email: "test@example.com",
        username: "testuser",
        password: "password123",
        traffic_limit_gb: 50,
        service_duration_days: 30
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
            console.log('✅ Success!');
            console.log('Connection URL:', result.vpn_config.connection_url);
        } else {
            console.error('❌ Error:', result.detail);
        }
    } catch (error) {
        console.error('Connection error:', error);
    }
};

registerCustomer();
```

---

## 2. Login

### Request

```bash
POST /login
Content-Type: application/json
```

```json
{
  "username": "customer1",
  "password": "securepass123"
}
```

### Response (200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer1",
    "password": "securepass123"
  }'
```

---

## 3. Get My VPN Configs

**Requires authentication**

### Request

```bash
GET /my-vpn-configs
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Response (200)

```json
[
  {
    "id": 1,
    "config_name": "customer1-xui_1",
    "protocol": "vless",
    "panel_type": "xui_1",
    "service_status": "active",
    "traffic_limit_gb": 50,
    "traffic_used_gb": 15,
    "activated_at": "2025-11-29T10:30:00",
    "expires_at": "2025-12-29T10:30:00",
    "connection_url": "vless://...",
    "subscription_url": null,
    "created_at": "2025-11-29T10:30:00"
  }
]
```

### cURL Example

```bash
TOKEN="your_access_token_here"

curl -X GET "http://localhost:8000/my-vpn-configs" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 4. Get VPN Config Stats

**Requires authentication**

### Request

```bash
GET /vpn-config/{config_id}/stats
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Response (200)

```json
{
  "config_id": 1,
  "stats": {
    "up": 1073741824,
    "down": 5368709120,
    "total": 6442450944
  },
  "traffic_limit_gb": 50,
  "traffic_used_gb": 6,
  "expires_at": "2025-12-29T10:30:00"
}
```

### cURL Example

```bash
TOKEN="your_access_token_here"

curl -X GET "http://localhost:8000/vpn-config/1/stats" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 5. Renew VPN Service

**Requires authentication**

### Request

```bash
POST /vpn-config/{config_id}/renew?additional_days=30&additional_traffic_gb=50
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Response (200)

```json
{
  "message": "Service renewed successfully",
  "config": {
    "id": 1,
    "expires_at": "2026-01-29T10:30:00",
    "traffic_limit_gb": 100,
    "service_status": "active"
  }
}
```

### cURL Example

```bash
TOKEN="your_access_token_here"

curl -X POST "http://localhost:8000/vpn-config/1/renew?additional_days=30&additional_traffic_gb=50" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. Check Available Panels

### Request

```bash
GET /panels
```

### Response (200)

```json
[
  {
    "panel_type": "xui_1",
    "is_enabled": true,
    "inbound_count": 3,
    "available": true
  },
  {
    "panel_type": "xui_2",
    "is_enabled": true,
    "inbound_count": 5,
    "available": true
  }
]
```

### cURL Example

```bash
curl -X GET "http://localhost:8000/panels"
```

---

## Complete Workflow Example

### 1. Check Available Panels

```bash
curl http://localhost:8000/panels
```

### 2. Register New Customer

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "john_doe",
    "password": "secure123",
    "traffic_limit_gb": 100,
    "service_duration_days": 30
  }' | jq
```

**Save the connection URL from response!**

### 3. Login to Get Token

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure123"
  }' | jq -r '.access_token'
```

**Copy the access_token**

### 4. View My Configs

```bash
TOKEN="paste_your_token_here"

curl -X GET "http://localhost:8000/my-vpn-configs" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 5. Check Usage

```bash
curl -X GET "http://localhost:8000/vpn-config/1/stats" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 6. Renew Service (when needed)

```bash
curl -X POST "http://localhost:8000/vpn-config/1/renew?additional_days=30&additional_traffic_gb=50" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid data) |
| 401 | Unauthorized (invalid token) |
| 404 | Not Found |
| 500 | Internal Server Error |

## Common Error Responses

### Invalid Credentials (401)

```json
{
  "detail": "Could not validate credentials"
}
```

### Customer Already Exists (400)

```json
{
  "detail": "Customer with this email or username already exists"
}
```

### Panel Not Available (500)

```json
{
  "detail": "Failed to create VPN configuration: Panel xui_1 is not available"
}
```

---

## Integration Tips

### 1. Webhook Integration

Sau khi khách hàng thanh toán thành công, gọi `/register` endpoint:

```python
# In your payment webhook handler
def handle_payment_success(payment_data):
    # Create VPN account automatically
    vpn_data = {
        "email": payment_data['customer_email'],
        "username": generate_username(payment_data['customer_email']),
        "password": generate_random_password(),
        "traffic_limit_gb": payment_data['package_traffic'],
        "service_duration_days": payment_data['package_days']
    }
    
    response = requests.post("http://localhost:8000/register", json=vpn_data)
    
    if response.status_code == 201:
        result = response.json()
        # Send connection URL to customer via email
        send_email(
            to=payment_data['customer_email'],
            subject="Your VPN is ready!",
            body=f"Connection URL: {result['vpn_config']['connection_url']}"
        )
```

### 2. WordPress Integration

```php
<?php
function create_vpn_account($email, $username, $password, $package) {
    $api_url = 'http://localhost:8000/register';
    
    $data = array(
        'email' => $email,
        'username' => $username,
        'password' => $password,
        'traffic_limit_gb' => $package['traffic'],
        'service_duration_days' => $package['days']
    );
    
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($data)
        )
    );
    
    $context  = stream_context_create($options);
    $result = file_get_contents($api_url, false, $context);
    
    return json_decode($result, true);
}
?>
```

---

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy"}`

### API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
