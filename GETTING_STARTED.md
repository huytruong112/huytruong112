# Getting Started Checklist

## ✅ Danh sách kiểm tra để bắt đầu

### Bước 1: Cài đặt môi trường ⏱️ 5 phút

- [ ] Python 3.8+ đã cài đặt
  ```bash
  python --version
  ```

- [ ] Chạy script setup
  ```bash
  ./scripts/setup.sh
  ```
  Hoặc manual:
  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### Bước 2: Cấu hình panel ⏱️ 5 phút

- [ ] Đã cài đặt x-ui hoặc 3x-ui panel
  - X-UI: `bash <(curl -Ls https://raw.githubusercontent.com/dopaemon/x-ui/main/install.sh)`
  - 3X-UI: `bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)`

- [ ] Panel đang chạy và có thể truy cập
  - Test: Mở trình duyệt, vào `http://your-server-ip:port`

- [ ] Đã tạo ít nhất 1 inbound trong panel
  - Vào panel → Inbounds → Add Inbound
  - Ghi nhớ inbound ID (thường là 1, 2, 3...)

- [ ] Biết username và password của panel

### Bước 3: Cấu hình ứng dụng ⏱️ 2 phút

- [ ] Copy file cấu hình
  ```bash
  cp .env.example .env
  ```

- [ ] Chỉnh sửa `.env` với thông tin panel
  ```bash
  nano .env
  ```

- [ ] Điền thông tin panel (ít nhất 1 trong 2):
  
  **Nếu dùng X-UI:**
  ```env
  XUI_PANEL_URL=http://your-server-ip:54321
  XUI_USERNAME=admin
  XUI_PASSWORD=your-password
  ```
  
  **Nếu dùng 3X-UI:**
  ```env
  THREEXUI_PANEL_URL=http://your-server-ip:2053
  THREEXUI_USERNAME=admin
  THREEXUI_PASSWORD=your-password
  ```

- [ ] Thay đổi secret key
  ```env
  API_SECRET_KEY=your-random-secret-key-here
  ```

### Bước 4: Kiểm tra cấu hình ⏱️ 2 phút

- [ ] Chạy script validation
  ```bash
  python scripts/validate_setup.py
  ```

- [ ] Tất cả checks phải pass ✅

- [ ] Nếu có lỗi, xem phần [Troubleshooting](#troubleshooting)

### Bước 5: Chạy API ⏱️ 1 phút

- [ ] Start API
  ```bash
  python main.py
  ```

- [ ] API running tại `http://localhost:8000`

- [ ] Kiểm tra health
  ```bash
  curl http://localhost:8000/health
  ```
  Kết quả mong đợi:
  ```json
  {
    "status": "healthy",
    "panels": {
      "x-ui_configured": true,
      "3x-ui_configured": false
    }
  }
  ```

### Bước 6: Kiểm tra API docs ⏱️ 2 phút

- [ ] Mở trình duyệt: `http://localhost:8000/docs`

- [ ] Xem danh sách endpoints

- [ ] Thử nghiệm với "Try it out"

### Bước 7: Tạo đăng ký đầu tiên ⏱️ 3 phút

- [ ] Chọn phương thức test:

**Option A: Qua Swagger UI**
1. Mở `http://localhost:8000/docs`
2. Tìm `POST /subscriptions`
3. Click "Try it out"
4. Điền thông tin:
   ```json
   {
     "customer_email": "test@example.com",
     "customer_name": "Test User",
     "panel_type": "xui",
     "inbound_id": 1,
     "traffic_limit_gb": 10,
     "expiry_days": 7
   }
   ```
5. Click "Execute"

**Option B: Qua curl**
```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "test@example.com",
    "customer_name": "Test User",
    "panel_type": "xui",
    "inbound_id": 1,
    "traffic_limit_gb": 10,
    "expiry_days": 7
  }'
```

**Option C: Qua Python script**
```bash
python examples/create_subscription_example.py
```

- [ ] Nhận được response với subscription ID

- [ ] Kiểm tra trong panel → Clients → Client mới đã được tạo

### Bước 8: Lấy cấu hình ⏱️ 1 phút

- [ ] Lấy config với subscription ID
  ```bash
  curl http://localhost:8000/subscriptions/1/config
  ```

- [ ] Nhận được thông tin cấu hình đầy đủ

### Bước 9: Test các chức năng khác ⏱️ 5 phút

- [ ] Xem chi tiết subscription
  ```bash
  curl http://localhost:8000/subscriptions/1
  ```

- [ ] Đồng bộ traffic
  ```bash
  curl -X POST http://localhost:8000/subscriptions/1/sync-traffic
  ```

- [ ] Gia hạn subscription
  ```bash
  curl -X POST http://localhost:8000/subscriptions/1/renew \
    -H "Content-Type: application/json" \
    -d '{"additional_days": 30}'
  ```

- [ ] Tạm ngưng subscription
  ```bash
  curl -X PUT http://localhost:8000/subscriptions/1 \
    -H "Content-Type: application/json" \
    -d '{"status": "suspended", "enable": false}'
  ```

- [ ] Kích hoạt lại
  ```bash
  curl -X PUT http://localhost:8000/subscriptions/1 \
    -H "Content-Type: application/json" \
    -d '{"status": "active", "enable": true}'
  ```

### Bước 10: Tích hợp với hệ thống của bạn ⏱️ Tùy dự án

- [ ] Đọc file `API_GUIDE.md` để hiểu rõ API

- [ ] Chọn phương thức tích hợp:
  - [ ] Website → Direct API calls
  - [ ] Payment Gateway → Webhook
  - [ ] Telegram → Bot
  - [ ] Discord → Bot
  - [ ] Mobile App → REST API

- [ ] Xem examples trong `/examples`:
  - `webhook_example.py` - Payment webhook
  - `telegram_bot_example.py` - Telegram bot
  - `create_subscription_example.py` - Basic usage

- [ ] Implement logic trong hệ thống của bạn

## 📋 Checklist trước khi deploy Production

### Security
- [ ] Thay đổi `API_SECRET_KEY` thành random string mạnh
- [ ] Thêm authentication (JWT/API Key)
- [ ] Enable HTTPS với SSL certificate
- [ ] Configure firewall
- [ ] Thay đổi default passwords của panels
- [ ] Restrict API access by IP (nếu cần)

### Performance
- [ ] Thêm rate limiting
- [ ] Configure proper timeout values
- [ ] Set up connection pooling
- [ ] Optimize database queries
- [ ] Add caching nếu cần

### Monitoring
- [ ] Set up logging
- [ ] Configure log rotation
- [ ] Add health check monitoring
- [ ] Set up alerts
- [ ] Monitor API response times
- [ ] Track error rates

### Backup
- [ ] Configure automatic database backups
- [ ] Test restore procedure
- [ ] Backup `.env` file securely
- [ ] Document recovery procedures

### Deployment
- [ ] Choose deployment method:
  - [ ] Direct Python with systemd
  - [ ] Docker with docker-compose
  - [ ] Kubernetes (for scale)
  - [ ] Cloud providers (AWS, GCP, Azure)
- [ ] Set up reverse proxy (nginx)
- [ ] Configure domain and DNS
- [ ] Test all endpoints in production
- [ ] Load testing

## 🐛 Troubleshooting

### ❌ Error: Cannot connect to panel

**Giải pháp:**
```bash
# 1. Check panel is running
systemctl status x-ui
# or
systemctl status 3x-ui

# 2. Test connection
curl http://your-panel-url

# 3. Check firewall
sudo ufw status
sudo ufw allow 54321  # for x-ui
sudo ufw allow 2053   # for 3x-ui

# 4. Verify credentials
# Login to panel via browser to test
```

### ❌ Error: Authentication failed

**Giải pháp:**
1. Verify username/password in `.env`
2. Try logging in via browser
3. Check for typos in `.env`
4. Ensure user has admin privileges

### ❌ Error: Inbound not found

**Giải pháp:**
1. Login to panel
2. Go to Inbounds
3. Check the ID number
4. Use correct ID in API call

### ❌ Error: Module not found

**Giải pháp:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### ❌ Error: Database locked

**Giải pháp:**
```bash
# Stop all processes using database
pkill -f main.py

# Remove database file
rm vpn_service.db

# Restart API
python main.py
```

### ❌ Error: Port already in use

**Giải pháp:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in .env
API_PORT=8001
```

## 📞 Cần hỗ trợ?

1. ✅ Đọc documentation trong các file:
   - `README.md` - Main docs
   - `QUICKSTART.md` - Quick start
   - `API_GUIDE.md` - API reference
   - `PROJECT_OVERVIEW.md` - Architecture

2. ✅ Chạy validation script:
   ```bash
   python scripts/validate_setup.py
   ```

3. ✅ Check logs:
   ```bash
   tail -f app.log
   ```

4. ✅ Test connections:
   ```bash
   python scripts/test_connection.py
   ```

5. ✅ Tạo issue trên GitHub với:
   - Error messages
   - Log output
   - Configuration (hide passwords!)
   - Steps to reproduce

## 🎓 Resources

### Documentation
- 📖 Full Vietnamese docs: `README.md`
- 📖 English docs: `README_EN.md`
- 📖 API Guide: `API_GUIDE.md`
- 📖 Quick Start: `QUICKSTART.md`
- 📖 Architecture: `PROJECT_OVERVIEW.md`

### Examples
- 💻 Basic usage: `examples/create_subscription_example.py`
- 💻 Webhook: `examples/webhook_example.py`
- 💻 Telegram Bot: `examples/telegram_bot_example.py`

### Tools
- 🔧 Setup: `scripts/setup.sh`
- 🔧 Validation: `scripts/validate_setup.py`
- 🔧 Test connection: `scripts/test_connection.py`

### External
- 🌐 X-UI GitHub: https://github.com/dopaemon/x-ui
- 🌐 3X-UI GitHub: https://github.com/mhsanaei/3x-ui
- 🌐 FastAPI Docs: https://fastapi.tiangolo.com

## ✅ Hoàn thành!

Khi bạn đã check hết tất cả boxes trên, bạn đã sẵn sàng để:

🎉 **Tự động tạo VPN subscriptions khi khách hàng đăng ký!**

Chúc bạn thành công! 🚀
