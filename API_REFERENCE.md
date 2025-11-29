# API Reference

Tài liệu chi tiết về các API endpoints.

## Base URL

```
http://your-server:8000
```

## Authentication

Tất cả các API endpoints yêu cầu API key trong header:

```
X-API-Key: your_secret_api_key
```

## Endpoints

### 1. Health Check

Kiểm tra trạng thái API server.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "xui_panels": 0,
  "threexui_panels": 2,
  "timestamp": "2024-11-29T10:30:00"
}
```

---

### 2. Register Customer

Đăng ký khách hàng mới và tự động tạo cấu hình VPN.

```http
POST /api/v1/customer/register
```

**Headers:**
```
X-API-Key: your_secret_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "customer@example.com",
  "name": "Nguyễn Văn A",
  "plan": "premium",
  "phone": "0123456789",
  "custom_config": {
    "total_gb": 300,
    "expiry_days": 60
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Email của khách hàng (unique) |
| name | string | Yes | Tên khách hàng |
| plan | string | Yes | Tên gói dịch vụ (basic, premium, enterprise) |
| phone | string | No | Số điện thoại |
| custom_config | object | No | Cấu hình tùy chỉnh, ghi đè cấu hình plan |

**Response Success (200):**
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
      "client_data": {
        "email": "customer@example.com",
        "total_gb": 200,
        "expiry_days": 30,
        "limit_ip": 5
      },
      "expiry_time": 1735565229000,
      "total_gb": 200
    },
    "created_at": "2024-11-29T10:30:00"
  }
}
```

**Response Error (500):**
```json
{
  "detail": "Không thể tạo cấu hình VPN, vui lòng thử lại"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/customer/register" \
  -H "X-API-Key: your_secret_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "name": "Nguyễn Văn A",
    "plan": "premium"
  }'
```

---

### 3. Get Customer Usage

Lấy thông tin sử dụng data và thời gian hết hạn của khách hàng.

```http
POST /api/v1/customer/usage
```

**Headers:**
```
X-API-Key: your_secret_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "customer@example.com",
  "panel_name": "server1"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Email của khách hàng |
| panel_name | string | No | Tên panel (nếu biết), nếu không có sẽ tìm trong tất cả panels |

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "email": "customer@example.com",
    "up": 5368709120,
    "down": 21474836480,
    "total": 107374182400,
    "expiryTime": 1735565229000,
    "enable": true
  }
}
```

**Response Error (404):**
```json
{
  "detail": "Không tìm thấy thông tin cho email: customer@example.com"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/customer/usage" \
  -H "X-API-Key: your_secret_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com"
  }'
```

---

### 4. Renew Customer

Gia hạn thời gian sử dụng cho khách hàng.

```http
POST /api/v1/customer/renew
```

**Headers:**
```
X-API-Key: your_secret_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "customer@example.com",
  "panel_name": "server1",
  "days": 30
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Email của khách hàng |
| panel_name | string | Yes | Tên panel (server1, server2, ...) |
| days | integer | No | Số ngày gia hạn (mặc định: 30) |

**Response Success (200):**
```json
{
  "success": true,
  "message": "Đã gia hạn 30 ngày cho customer@example.com"
}
```

**Response Error (500):**
```json
{
  "detail": "Không thể gia hạn, vui lòng thử lại"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/customer/renew" \
  -H "X-API-Key: your_secret_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "panel_name": "server1",
    "days": 30
  }'
```

---

### 5. Delete Customer

Xóa cấu hình VPN của khách hàng.

```http
DELETE /api/v1/customer/delete
```

**Headers:**
```
X-API-Key: your_secret_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "customer@example.com",
  "panel_name": "server1",
  "inbound_id": 1
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Email của khách hàng |
| panel_name | string | Yes | Tên panel |
| inbound_id | integer | No | ID của inbound (cần cho 3x-ui) |

**Response Success (200):**
```json
{
  "success": true,
  "message": "Đã xóa cấu hình cho customer@example.com"
}
```

**Response Error (404):**
```json
{
  "detail": "Không tìm thấy khách hàng để xóa"
}
```

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/customer/delete" \
  -H "X-API-Key: your_secret_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "panel_name": "server1",
    "inbound_id": 1
  }'
```

---

### 6. Get Plans

Lấy danh sách các gói dịch vụ có sẵn.

```http
GET /api/v1/plans
```

**Headers:**
```
X-API-Key: your_secret_api_key
```

**Response Success (200):**
```json
{
  "success": true,
  "plans": {
    "basic": {
      "panel_type": "3x-ui",
      "data_limit_gb": 50,
      "duration_days": 30,
      "protocol": "vmess",
      "network": "tcp",
      "security": "none",
      "limit_ip": 2
    },
    "premium": {
      "panel_type": "3x-ui",
      "data_limit_gb": 200,
      "duration_days": 30,
      "protocol": "vmess",
      "network": "ws",
      "security": "tls",
      "limit_ip": 5
    },
    "enterprise": {
      "panel_type": "3x-ui",
      "data_limit_gb": 500,
      "duration_days": 30,
      "protocol": "vless",
      "network": "grpc",
      "security": "tls",
      "limit_ip": 0
    }
  }
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/plans" \
  -H "X-API-Key: your_secret_api_key"
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 403 | Invalid API Key |
| 404 | Resource not found |
| 500 | Internal server error |

## Error Response Format

```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Hiện tại chưa có rate limiting. Khuyến nghị implement rate limiting ở reverse proxy (Nginx).

## Data Format

### Timestamps
- Tất cả timestamps đều ở dạng milliseconds (Unix timestamp * 1000)
- Ví dụ: `1735565229000` = 2024-12-30 10:47:09

### Data Size
- Tất cả data size đều ở dạng bytes
- 1 GB = 1,073,741,824 bytes

### Email
- Phải là email hợp lệ
- Unique trong mỗi panel

## Webhook Integration

Để tích hợp với payment gateway, bạn có thể:

1. Thiết lập webhook URL trỏ đến endpoint của bạn
2. Trong webhook handler, gọi API `/api/v1/customer/register`
3. Xử lý response và thông báo cho khách hàng

Xem ví dụ trong `examples/` folder.

## Best Practices

1. **Always validate email** trước khi gọi API
2. **Store panel_name** khi tạo khách hàng để dễ quản lý sau này
3. **Handle errors gracefully** và có retry logic
4. **Log all API calls** để audit trail
5. **Secure your API key** - không commit vào git
6. **Use HTTPS** trong production
7. **Implement rate limiting** ở reverse proxy
8. **Monitor API health** bằng `/health` endpoint

## Interactive Documentation

Truy cập `http://your-server:8000/docs` để xem Swagger UI với:
- Interactive API testing
- Schema definitions
- Example requests/responses
