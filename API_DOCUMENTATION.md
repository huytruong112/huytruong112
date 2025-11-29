# 📚 API Documentation

Tài liệu đầy đủ về các API endpoint của hệ thống quản lý X-UI/3X-UI.

## Base URL

```
http://localhost:5000/api
```

Trong production, thay thế bằng domain của bạn.

## Endpoints

### Health Check

#### GET /api/health

Kiểm tra trạng thái API.

**Response:**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

---

## Customers (Khách hàng)

### 1. Lấy danh sách khách hàng

#### GET /api/customers

Lấy tất cả khách hàng.

**Response:**
```json
{
  "success": true,
  "customers": [
    {
      "id": 1,
      "email": "customer@example.com",
      "name": "Nguyễn Văn A",
      "phone": "+84123456789",
      "telegram_id": "@username",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00",
      "updated_at": "2025-01-01T00:00:00",
      "subscriptions": [...]
    }
  ]
}
```

### 2. Lấy chi tiết khách hàng

#### GET /api/customers/{customer_id}

**Parameters:**
- `customer_id` (path): ID của khách hàng

**Response:**
```json
{
  "success": true,
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "name": "Nguyễn Văn A",
    "phone": "+84123456789",
    "telegram_id": "@username",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00",
    "subscriptions": [...]
  }
}
```

### 3. Tạo khách hàng mới

#### POST /api/customers

**Request Body:**
```json
{
  "email": "customer@example.com",
  "name": "Nguyễn Văn A",
  "phone": "+84123456789",
  "telegram_id": "@username"
}
```

**Required fields:**
- `email`: Email khách hàng (unique)
- `name`: Tên khách hàng

**Response:**
```json
{
  "success": true,
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "name": "Nguyễn Văn A",
    "phone": "+84123456789",
    "telegram_id": "@username",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00",
    "subscriptions": []
  }
}
```

### 4. Cập nhật khách hàng

#### PUT /api/customers/{customer_id}

**Parameters:**
- `customer_id` (path): ID của khách hàng

**Request Body:**
```json
{
  "name": "Nguyễn Văn B",
  "phone": "+84987654321",
  "telegram_id": "@newusername",
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "name": "Nguyễn Văn B",
    ...
  }
}
```

### 5. Xóa khách hàng

#### DELETE /api/customers/{customer_id}

Xóa khách hàng và tất cả subscriptions của họ.

**Parameters:**
- `customer_id` (path): ID của khách hàng

**Response:**
```json
{
  "success": true,
  "message": "Customer deleted successfully"
}
```

---

## Subscriptions (Gói dịch vụ)

### 1. Tạo subscription mới

#### POST /api/subscriptions

Tạo subscription mới cho khách hàng có sẵn.

**Request Body:**
```json
{
  "customer_id": 1,
  "service_name": "Basic Plan",
  "traffic_limit_gb": 100,
  "expiry_days": 30,
  "inbound_id": 1
}
```

**Parameters:**
- `customer_id` (required): ID khách hàng
- `service_name`: Tên gói dịch vụ (mặc định: "Standard Plan")
- `traffic_limit_gb`: Giới hạn dung lượng GB (0 = unlimited, mặc định: 100)
- `expiry_days`: Số ngày hết hạn (0 = không hết hạn, mặc định: 30)
- `inbound_id`: ID của inbound trên panel (mặc định: 1)

**Response:**
```json
{
  "success": true,
  "subscription": {
    "id": 1,
    "customer_id": 1,
    "uuid": "12345678-1234-1234-1234-123456789abc",
    "inbound_id": 1,
    "service_name": "Basic Plan",
    "traffic_limit_gb": 100,
    "traffic_used_gb": 0.0,
    "start_date": "2025-01-01T00:00:00",
    "expiry_date": "2025-01-31T00:00:00",
    "is_active": true,
    "is_expired": false,
    "notes": null,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  },
  "message": "Subscription created successfully"
}
```

### 2. Lấy chi tiết subscription

#### GET /api/subscriptions/{subscription_id}

**Parameters:**
- `subscription_id` (path): ID của subscription

**Response:**
```json
{
  "success": true,
  "subscription": {
    "id": 1,
    "customer_id": 1,
    "uuid": "12345678-1234-1234-1234-123456789abc",
    "inbound_id": 1,
    "service_name": "Basic Plan",
    "traffic_limit_gb": 100,
    "traffic_used_gb": 25.5,
    ...
  }
}
```

### 3. Cập nhật subscription

#### PUT /api/subscriptions/{subscription_id}

**Parameters:**
- `subscription_id` (path): ID của subscription

**Request Body:**
```json
{
  "service_name": "Premium Plan",
  "traffic_limit_gb": 200,
  "expiry_days": 60,
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "subscription": {
    "id": 1,
    "service_name": "Premium Plan",
    "traffic_limit_gb": 200,
    ...
  }
}
```

### 4. Xóa subscription

#### DELETE /api/subscriptions/{subscription_id}

Xóa subscription và cấu hình trên panel.

**Parameters:**
- `subscription_id` (path): ID của subscription

**Response:**
```json
{
  "success": true,
  "message": "Subscription deleted successfully"
}
```

### 5. Xem traffic của subscription

#### GET /api/subscriptions/{subscription_id}/traffic

Lấy thông tin traffic thời gian thực từ panel.

**Parameters:**
- `subscription_id` (path): ID của subscription

**Response:**
```json
{
  "success": true,
  "traffic": {
    "download_gb": 10.5,
    "upload_gb": 5.2,
    "total_gb": 15.7,
    "limit_gb": 100,
    "remaining_gb": 84.3
  }
}
```

### 6. Reset traffic (chỉ 3X-UI)

#### POST /api/subscriptions/{subscription_id}/reset-traffic

Reset traffic counter về 0.

**Parameters:**
- `subscription_id` (path): ID của subscription

**Response:**
```json
{
  "success": true,
  "message": "Traffic reset successfully"
}
```

---

## Registration (Đăng ký hoàn chỉnh)

### Đăng ký khách hàng + Tạo subscription

#### POST /api/register

Endpoint đặc biệt để tạo khách hàng mới và subscription trong một request. Tự động tạo cấu hình trên panel.

**Request Body:**
```json
{
  "email": "customer@example.com",
  "name": "Nguyễn Văn A",
  "phone": "+84123456789",
  "telegram_id": "@username",
  "service_name": "Basic Plan",
  "traffic_limit_gb": 100,
  "expiry_days": 30,
  "inbound_id": 1
}
```

**Required fields:**
- `email`: Email khách hàng
- `name`: Tên khách hàng

**Response:**
```json
{
  "success": true,
  "customer": {
    "id": 1,
    "email": "customer@example.com",
    "name": "Nguyễn Văn A",
    ...
  },
  "subscription": {
    "id": 1,
    "uuid": "12345678-1234-1234-1234-123456789abc",
    "service_name": "Basic Plan",
    "traffic_limit_gb": 100,
    ...
  },
  "message": "Registration completed successfully"
}
```

---

## Inbounds

### Lấy danh sách inbounds

#### GET /api/inbounds

Lấy danh sách tất cả inbounds từ panel.

**Response:**
```json
{
  "success": true,
  "inbounds": [
    {
      "id": 1,
      "port": 443,
      "protocol": "vless",
      "settings": {...},
      ...
    }
  ]
}
```

---

## Error Responses

Tất cả các endpoint có thể trả về error response:

```json
{
  "success": false,
  "error": "Error message here"
}
```

**HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

---

## Examples

### Python Example

```python
import requests

# Đăng ký khách hàng mới
response = requests.post(
    'http://localhost:5000/api/register',
    json={
        'email': 'test@example.com',
        'name': 'Test User',
        'service_name': 'Basic Plan',
        'traffic_limit_gb': 100,
        'expiry_days': 30
    }
)

result = response.json()
if result['success']:
    print(f"UUID: {result['subscription']['uuid']}")
    print(f"Expiry: {result['subscription']['expiry_date']}")
```

### JavaScript Example

```javascript
// Đăng ký khách hàng mới
const registerCustomer = async (data) => {
  const response = await fetch('http://localhost:5000/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('UUID:', result.subscription.uuid);
    console.log('Customer ID:', result.customer.id);
  } else {
    console.error('Error:', result.error);
  }
};

// Sử dụng
registerCustomer({
  email: 'test@example.com',
  name: 'Test User',
  service_name: 'Premium Plan',
  traffic_limit_gb: 200,
  expiry_days: 60
});
```

### cURL Examples

```bash
# Đăng ký khách hàng mới
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "service_name": "Basic Plan",
    "traffic_limit_gb": 100,
    "expiry_days": 30
  }'

# Xem traffic
curl http://localhost:5000/api/subscriptions/1/traffic

# Xóa subscription
curl -X DELETE http://localhost:5000/api/subscriptions/1

# Lấy danh sách khách hàng
curl http://localhost:5000/api/customers
```

---

## Webhook Integration

Bạn có thể sử dụng API này làm webhook cho payment gateway:

```javascript
// Ví dụ: Stripe webhook handler
app.post('/webhook/stripe', async (req, res) => {
  const event = req.body;
  
  if (event.type === 'payment_intent.succeeded') {
    const payment = event.data.object;
    
    // Tạo VPN account tự động
    const response = await fetch('http://localhost:5000/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: payment.customer_email,
        name: payment.customer_name,
        service_name: payment.metadata.plan,
        traffic_limit_gb: parseInt(payment.metadata.traffic_gb),
        expiry_days: parseInt(payment.metadata.days)
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Gửi email cho khách hàng
      sendVPNConfigEmail(result.customer, result.subscription);
    }
  }
  
  res.json({ received: true });
});
```

---

## Rate Limiting

Hiện tại chưa có rate limiting. Trong production, nên thêm rate limiting để bảo vệ API.

## Authentication

Hiện tại API không có authentication. Trong production, nên thêm:
- JWT tokens
- API keys
- OAuth 2.0

## Support

Nếu có câu hỏi về API, vui lòng tạo issue trên GitHub repository.
