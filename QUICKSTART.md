# Quick Start Guide

Hướng dẫn nhanh để chạy hệ thống trong 5 phút!

## 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## 2. Tạo config

```bash
cp config.example.json config.json
nano config.json
```

Sửa các thông tin quan trọng:
- `url`: Địa chỉ panel của bạn
- `username` và `password`: Thông tin đăng nhập
- `default_inbound_id`: ID của inbound (xem trong panel)
- `api_key`: Tạo một string ngẫu nhiên

## 3. Test kết nối

```bash
python3 test_connection.py
```

Đợi cho đến khi thấy "✅ Tất cả tests đều PASS"

## 4. Chạy API server

```bash
python3 api_server.py
```

API sẽ chạy tại `http://localhost:8000`

## 5. Test API

Mở terminal mới và chạy:

```bash
# Xem Swagger docs
open http://localhost:8000/docs

# Hoặc test bằng curl
curl -X POST "http://localhost:8000/api/v1/customer/register" \
  -H "X-API-Key: your_api_key_from_config" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "plan": "basic"
  }'
```

## 6. Tích hợp với website

Xem các ví dụ trong thư mục `examples/`:
- `php_integration.php` - Cho PHP/WordPress/Laravel
- `nodejs_integration.js` - Cho Node.js/Express
- `python_integration.py` - Cho Python/Flask/Django

## API Endpoints

### Đăng ký khách hàng mới
```
POST /api/v1/customer/register
Header: X-API-Key: your_key
Body: {
  "email": "customer@example.com",
  "name": "Customer Name",
  "plan": "basic"
}
```

### Kiểm tra usage
```
POST /api/v1/customer/usage
Header: X-API-Key: your_key
Body: {
  "email": "customer@example.com"
}
```

### Gia hạn
```
POST /api/v1/customer/renew
Header: X-API-Key: your_key
Body: {
  "email": "customer@example.com",
  "panel_name": "server1",
  "days": 30
}
```

### Xóa khách hàng
```
DELETE /api/v1/customer/delete
Header: X-API-Key: your_key
Body: {
  "email": "customer@example.com",
  "panel_name": "server1",
  "inbound_id": 1
}
```

## Các Plans Mặc Định

- **basic**: 50GB/30 ngày, 2 thiết bị
- **premium**: 200GB/30 ngày, 5 thiết bị
- **enterprise**: 500GB/30 ngày, không giới hạn thiết bị

Bạn có thể thay đổi trong `config.json`

## Troubleshooting

**Không kết nối được panel?**
- Kiểm tra URL có đúng không (http/https, port)
- Kiểm tra firewall có block không
- Test bằng browser: mở URL panel

**Login failed?**
- Kiểm tra username/password
- Thử đăng nhập vào panel bằng browser

**Inbound not found?**
- Chạy `python3 test_connection.py` để xem available IDs
- Tạo inbound mới trong panel nếu cần

## Tài Liệu Đầy Đủ

- [README.md](README.md) - Tài liệu đầy đủ
- [INSTALLATION.md](INSTALLATION.md) - Hướng dẫn cài đặt chi tiết
- `examples/` - Các ví dụ tích hợp

## Support

Có vấn đề? Kiểm tra:
1. Config file có đúng không
2. Panel có đang chạy không
3. Logs của API: xem trong terminal
