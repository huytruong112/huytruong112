# 🚀 Quick Start Guide

Hướng dẫn nhanh để chạy hệ thống trong 5 phút!

## ✅ Prerequisites

- Python 3.8 trở lên
- x-ui hoặc 3x-ui panel đã cài đặt và chạy

## 📦 Installation

### Bước 1: Clone/Download code

```bash
# Nếu dùng git
git clone <your-repo-url>
cd <directory>

# Hoặc download và giải nén
```

### Bước 2: Cài đặt dependencies

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Bước 3: Cấu hình

```bash
cp .env.example .env
nano .env  # Hoặc dùng editor bất kỳ
```

**Cấu hình tối thiểu trong `.env`:**

```env
# Panel Configuration
XUI_2_URL=http://your-server-ip:2053
XUI_2_USERNAME=admin
XUI_2_PASSWORD=your-password
XUI_2_ENABLED=true

# Security
SECRET_KEY=change-this-to-random-string
```

### Bước 4: Chạy

```bash
python main.py
```

Hoặc:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🎯 Test ngay

### 1. Kiểm tra health

```bash
curl http://localhost:8000/health
```

Kết quả: `{"status":"healthy"}`

### 2. Kiểm tra panels

```bash
curl http://localhost:8000/panels
```

### 3. Đăng ký test customer

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "test123456",
    "traffic_limit_gb": 50,
    "service_duration_days": 30
  }'
```

**Nếu thành công, bạn sẽ nhận được connection URL ngay lập tức! 🎉**

### 4. Mở Web UI

Mở file `example_register.html` trong trình duyệt để có giao diện đẹp.

**Lưu ý:** Sửa dòng này trong file HTML:
```javascript
const API_URL = 'http://localhost:8000';  // Đổi thành URL server của bạn
```

## 📚 Next Steps

1. **Xem API Documentation**: http://localhost:8000/docs
2. **Đọc hướng dẫn chi tiết**: [SETUP_GUIDE_VI.md](SETUP_GUIDE_VI.md)
3. **Xem API examples**: [API_EXAMPLES.md](API_EXAMPLES.md)
4. **Tích hợp vào website**: Xem phần Integration trong README.md

## 🔧 Troubleshooting

### Lỗi: Panel không kết nối được

```bash
# Kiểm tra panel có chạy không
curl http://your-panel-ip:2053

# Kiểm tra cấu hình .env
cat .env | grep XUI
```

### Lỗi: Module not found

```bash
# Cài lại dependencies
pip install -r requirements.txt
```

### Lỗi: Port 8000 đã được sử dụng

```bash
# Đổi port khác
uvicorn main:app --host 0.0.0.0 --port 8080
```

## 🐳 Docker (Alternative)

Nếu muốn dùng Docker:

```bash
# Build
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs
2. Đọc [SETUP_GUIDE_VI.md](SETUP_GUIDE_VI.md) 
3. Xem [API_EXAMPLES.md](API_EXAMPLES.md)
4. Tạo issue trên GitHub

---

**Chúc bạn thành công! 🚀**
