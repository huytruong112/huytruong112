# 🚀 BẮT ĐẦU TỪ ĐÂY

## Chào mừng bạn đến với VPN Subscription Management System!

### 🎯 Hệ thống này làm gì?

**Giải quyết vấn đề của bạn:** Tự động tạo cấu hình VPN trong x-ui hoặc 3x-ui khi khách hàng đăng ký dịch vụ.

**Workflow:**
```
Khách hàng thanh toán → API tự động tạo → Client trong panel → Khách hàng nhận config
```

### ⚡ Quick Start (3 lệnh)

```bash
# 1. Setup
./scripts/setup.sh

# 2. Cấu hình panel trong .env
nano .env

# 3. Chạy
python main.py
```

Truy cập: http://localhost:8000/docs

### 📚 Đọc gì tiếp theo?

#### Bắt đầu nhanh (Khuyến nghị)
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** ← BẮT ĐẦU TẠI ĐÂY
   - Checklist từng bước
   - Setup, config, test
   - Troubleshooting

2. **[QUICKSTART.md](QUICKSTART.md)**
   - Hướng dẫn nhanh
   - Các lệnh cơ bản
   - Ví dụ sử dụng

#### Documentation chi tiết
3. **[README.md](README.md)** (Tiếng Việt)
   - Documentation đầy đủ
   - Tính năng
   - Cài đặt và sử dụng

4. **[API_GUIDE.md](API_GUIDE.md)**
   - API reference chi tiết
   - Tất cả endpoints
   - Examples với nhiều ngôn ngữ

5. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**
   - Kiến trúc hệ thống
   - Component chi tiết
   - Use cases

6. **[SUMMARY.md](SUMMARY.md)**
   - Tóm tắt dự án
   - Tính năng đã hoàn thành
   - Hướng dẫn tích hợp

#### English version
7. **[README_EN.md](README_EN.md)**
   - Full English documentation

### 🔧 Scripts có sẵn

```bash
# Setup tự động
./scripts/setup.sh

# Kiểm tra cấu hình
python scripts/validate_setup.py

# Test kết nối với panels
python scripts/test_connection.py
```

### 💡 Examples

```bash
# Tạo subscription
python examples/create_subscription_example.py

# Payment webhook server
python examples/webhook_example.py

# Telegram bot
python examples/telegram_bot_example.py
```

### 📁 Cấu trúc project

```
/workspace/
├── 📖 Documentation
│   ├── START_HERE.md          ← Bạn đang đọc file này
│   ├── GETTING_STARTED.md     ← Checklist từng bước
│   ├── QUICKSTART.md          ← Quick start guide
│   ├── README.md              ← Main docs (VI)
│   ├── README_EN.md           ← English docs
│   ├── API_GUIDE.md           ← API reference
│   ├── PROJECT_OVERVIEW.md    ← Architecture
│   └── SUMMARY.md             ← Project summary
│
├── 🔧 Scripts
│   ├── scripts/setup.sh           ← Automatic setup
│   ├── scripts/validate_setup.py  ← Validate config
│   └── scripts/test_connection.py ← Test panels
│
├── 💻 Examples
│   ├── examples/create_subscription_example.py
│   ├── examples/webhook_example.py
│   └── examples/telegram_bot_example.py
│
├── 🏗️ Application Code
│   ├── main.py                ← FastAPI app
│   ├── config.py              ← Configuration
│   ├── models.py              ← Database models
│   ├── database.py            ← Database config
│   ├── schemas.py             ← Pydantic schemas
│   ├── clients/               ← Panel API clients
│   │   ├── xui_client.py
│   │   └── threexui_client.py
│   └── services/              ← Business logic
│       └── vpn_service.py
│
├── 🐳 Deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── .env.example
│
└── ⚙️ Config
    ├── .env.example           ← Copy to .env
    └── .gitignore
```

### 🎯 Bước tiếp theo

#### Nếu bạn mới bắt đầu:
1. Đọc **[GETTING_STARTED.md](GETTING_STARTED.md)**
2. Follow checklist từng bước
3. Tạo subscription đầu tiên
4. Xem kết quả trong panel

#### Nếu bạn muốn tích hợp:
1. Đọc **[API_GUIDE.md](API_GUIDE.md)**
2. Xem examples trong `/examples`
3. Choose integration method:
   - Website → Direct API calls
   - Payment → Webhook
   - Telegram → Bot

#### Nếu bạn muốn deploy:
1. Đọc phần deployment trong **[README.md](README.md)**
2. Choose method: Docker / systemd / nginx
3. Follow security checklist
4. Set up monitoring

### 🔑 Key Features

✅ **Auto-create VPN configs** khi khách hàng đăng ký
✅ **Support both x-ui và 3x-ui** panels
✅ **RESTful API** với FastAPI
✅ **Complete CRUD** operations
✅ **Traffic tracking** và sync
✅ **Auto expiry** management
✅ **QR code generation**
✅ **Webhook ready** cho payment integration
✅ **Examples** cho mọi use case
✅ **Production ready** với Docker support

### 💻 API Endpoints

```
POST   /subscriptions          → Tạo subscription mới
GET    /subscriptions/{id}     → Xem chi tiết
GET    /subscriptions/{id}/config → Lấy cấu hình
POST   /subscriptions/{id}/renew → Gia hạn
PUT    /subscriptions/{id}     → Cập nhật trạng thái
DELETE /subscriptions/{id}     → Xóa
POST   /subscriptions/{id}/sync-traffic → Đồng bộ traffic
```

Xem đầy đủ tại: http://localhost:8000/docs

### 🎓 Use Cases

- **VPN Service Provider**: Auto provision accounts
- **Corporate**: Employee VPN management
- **Educational**: Student access management
- **Reseller**: White-label VPN service

### 🆘 Cần help?

1. ✅ Check **[GETTING_STARTED.md](GETTING_STARTED.md)** - Troubleshooting section
2. ✅ Run validation: `python scripts/validate_setup.py`
3. ✅ Check logs: `tail -f app.log`
4. ✅ Test connection: `python scripts/test_connection.py`

### 📞 Support

- 📖 Documentation trong thư mục
- 💻 Examples trong `/examples`
- 🔧 Tools trong `/scripts`
- 🌐 GitHub Issues

### 🎉 Sẵn sàng bắt đầu?

➡️ **[Mở GETTING_STARTED.md](GETTING_STARTED.md)** và follow checklist!

---

**Made with ❤️ for automated VPN subscription management**

🚀 Start automating your VPN subscriptions now!
