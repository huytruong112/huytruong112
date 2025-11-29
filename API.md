# 📚 API Documentation

## Base URL

```
http://localhost:3000
```

## Authentication

Hầu hết các endpoints yêu cầu JWT token trong header:

```
Authorization: Bearer <token>
```

Token được nhận sau khi đăng ký hoặc đăng nhập.

---

## Customer APIs

### 1. Lấy danh sách gói dịch vụ

**Endpoint:** `GET /api/packages`

**Authentication:** Không yêu cầu

**Response:**
```json
{
  "packages": [
    {
      "id": 1,
      "name": "Gói Cơ Bản",
      "description": "Phù hợp cho người dùng cá nhân",
      "duration_days": 30,
      "data_limit_gb": 50,
      "price": 50000,
      "max_connections": 1,
      "created_at": "2023-11-29T00:00:00.000Z"
    }
  ]
}
```

---

### 2. Đăng ký tài khoản

**Endpoint:** `POST /api/register`

**Authentication:** Không yêu cầu

**Request Body:**
```json
{
  "name": "Nguyen Van A",
  "email": "user@example.com",
  "phone": "0123456789",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "customerId": 1,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Đăng ký thành công"
}
```

**Error Response:**
```json
{
  "error": "Email đã tồn tại"
}
```

---

### 3. Đăng nhập

**Endpoint:** `POST /api/login`

**Authentication:** Không yêu cầu

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "customer": {
    "id": 1,
    "email": "user@example.com",
    "name": "Nguyen Van A",
    "phone": "0123456789"
  }
}
```

---

### 4. Tạo đơn hàng (Mua gói dịch vụ)

**Endpoint:** `POST /api/orders`

**Authentication:** Yêu cầu

**Request Body:**
```json
{
  "packageId": 1,
  "paymentMethod": "manual"
}
```

**Response:**
```json
{
  "success": true,
  "orderId": 1,
  "clientId": 1,
  "connectionUrl": "vless://uuid@server:port...",
  "subscriptionUrl": "http://server:2053/sub/xxxxx",
  "expiryDate": "2023-12-29T00:00:00.000Z",
  "message": "Đơn hàng đã được tạo và kích hoạt thành công"
}
```

**Error Response:**
```json
{
  "error": "Không tìm thấy gói dịch vụ"
}
```

---

### 5. Lấy danh sách dịch vụ của tôi

**Endpoint:** `GET /api/my-services`

**Authentication:** Yêu cầu

**Response:**
```json
{
  "services": [
    {
      "id": 1,
      "order_id": 1,
      "customer_id": 1,
      "client_id": "uuid-here",
      "email": "user@example.com",
      "connection_url": "vless://uuid@server:port...",
      "subscription_url": "http://server:2053/sub/xxxxx",
      "expiry_date": "2023-12-29T00:00:00.000Z",
      "data_limit_gb": 50,
      "status": "active",
      "created_at": "2023-11-29T00:00:00.000Z",
      "package_name": "Gói Cơ Bản",
      "package_description": "Phù hợp cho người dùng cá nhân",
      "order_date": "2023-11-29T00:00:00.000Z"
    }
  ]
}
```

---

### 6. Lấy thông tin chi tiết client

**Endpoint:** `GET /api/client/:clientId/info`

**Authentication:** Yêu cầu

**Response:**
```json
{
  "id": 1,
  "order_id": 1,
  "customer_id": 1,
  "client_id": "uuid-here",
  "email": "user@example.com",
  "connection_url": "vless://uuid@server:port...",
  "subscription_url": "http://server:2053/sub/xxxxx",
  "expiry_date": "2023-12-29T00:00:00.000Z",
  "data_limit_gb": 50,
  "status": "active",
  "traffic": {
    "up": 1024000,
    "down": 5120000,
    "total": 53687091200
  },
  "enable": true
}
```

---

## Admin APIs

### 1. Thống kê tổng quan

**Endpoint:** `GET /admin/api/stats`

**Response:**
```json
{
  "totalCustomers": 10,
  "totalOrders": 25,
  "totalRevenue": 1250000,
  "activeClients": 20
}
```

---

### 2. Danh sách khách hàng

**Endpoint:** `GET /admin/api/customers`

**Response:**
```json
{
  "customers": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "Nguyen Van A",
      "phone": "0123456789",
      "created_at": "2023-11-29T00:00:00.000Z",
      "total_orders": 2,
      "total_clients": 2
    }
  ]
}
```

---

### 3. Danh sách đơn hàng

**Endpoint:** `GET /admin/api/orders`

**Response:**
```json
{
  "orders": [
    {
      "id": 1,
      "customer_id": 1,
      "package_id": 1,
      "status": "paid",
      "payment_method": "manual",
      "total_amount": 50000,
      "created_at": "2023-11-29T00:00:00.000Z",
      "paid_at": "2023-11-29T00:00:00.000Z",
      "customer_name": "Nguyen Van A",
      "customer_email": "user@example.com",
      "package_name": "Gói Cơ Bản"
    }
  ]
}
```

---

### 4. Danh sách clients

**Endpoint:** `GET /admin/api/clients`

**Response:**
```json
{
  "clients": [
    {
      "id": 1,
      "order_id": 1,
      "customer_id": 1,
      "client_id": "uuid-here",
      "email": "user@example.com",
      "connection_url": "vless://uuid@server:port...",
      "subscription_url": "http://server:2053/sub/xxxxx",
      "expiry_date": "2023-12-29T00:00:00.000Z",
      "data_limit_gb": 50,
      "status": "active",
      "customer_name": "Nguyen Van A",
      "customer_email": "user@example.com",
      "traffic": {
        "up": 1024000,
        "down": 5120000,
        "total": 53687091200
      },
      "enable": true
    }
  ]
}
```

---

### 5. Tạo gói dịch vụ mới

**Endpoint:** `POST /admin/api/packages`

**Request Body:**
```json
{
  "name": "Gói VIP",
  "description": "Gói cao cấp nhất",
  "duration_days": 30,
  "data_limit_gb": 0,
  "price": 200000,
  "max_connections": 5
}
```

**Response:**
```json
{
  "success": true,
  "packageId": 6,
  "message": "Tạo gói dịch vụ thành công"
}
```

---

### 6. Cập nhật gói dịch vụ

**Endpoint:** `PUT /admin/api/packages/:id`

**Request Body:**
```json
{
  "name": "Gói VIP Updated",
  "description": "Mô tả mới",
  "duration_days": 30,
  "data_limit_gb": 0,
  "price": 180000,
  "max_connections": 5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cập nhật gói dịch vụ thành công"
}
```

---

### 7. Xóa gói dịch vụ

**Endpoint:** `DELETE /admin/api/packages/:id`

**Response:**
```json
{
  "success": true,
  "message": "Xóa gói dịch vụ thành công"
}
```

---

### 8. Vô hiệu hóa client

**Endpoint:** `POST /admin/api/clients/:clientId/disable`

**Response:**
```json
{
  "success": true,
  "message": "Đã vô hiệu hóa client"
}
```

---

### 9. Kích hoạt lại client

**Endpoint:** `POST /admin/api/clients/:clientId/enable`

**Response:**
```json
{
  "success": true,
  "message": "Đã kích hoạt lại client"
}
```

---

### 10. Xóa client

**Endpoint:** `DELETE /admin/api/clients/:clientId`

**Response:**
```json
{
  "success": true,
  "message": "Đã xóa client"
}
```

---

## Error Responses

Tất cả endpoints có thể trả về các lỗi sau:

### 400 Bad Request
```json
{
  "error": "Thiếu thông tin bắt buộc"
}
```

### 401 Unauthorized
```json
{
  "error": "Thiếu token xác thực"
}
```

### 403 Forbidden
```json
{
  "error": "Token không hợp lệ"
}
```

### 404 Not Found
```json
{
  "error": "Không tìm thấy resource"
}
```

### 500 Internal Server Error
```json
{
  "error": "Lỗi server",
  "details": "Chi tiết lỗi..."
}
```

---

## Rate Limiting

Hiện tại chưa có rate limiting. Trong production nên thêm:

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 phút
  max: 100 // giới hạn 100 requests
});

app.use('/api/', limiter);
```

---

## Webhooks

### Payment Callback (VNPay)

**Endpoint:** `GET /api/payment/vnpay/callback`

**Query Parameters:**
- `vnp_TxnRef`: Order ID
- `vnp_ResponseCode`: Mã kết quả
- `vnp_SecureHash`: Chữ ký

**Response:** Redirect đến trang success/failed

---

### Payment IPN (MoMo)

**Endpoint:** `POST /api/payment/momo/ipn`

**Request Body:**
```json
{
  "orderId": "1",
  "resultCode": 0,
  "signature": "..."
}
```

**Response:** 204 No Content

---

## Testing với curl

### Đăng ký
```bash
curl -X POST http://localhost:3000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

### Đăng nhập
```bash
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Lấy gói dịch vụ
```bash
curl http://localhost:3000/api/packages
```

### Mua gói (cần token)
```bash
curl -X POST http://localhost:3000/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"packageId":1,"paymentMethod":"manual"}'
```

---

## Postman Collection

Bạn có thể import các endpoints trên vào Postman để test dễ dàng hơn.

---

Để biết thêm chi tiết, vui lòng xem source code trong thư mục `routes/`.
