# 🚀 Hệ thống Quản lý X-UI/3X-UI Tự động

Hệ thống tự động quản lý và tạo cấu hình cho khách hàng đăng ký dịch vụ VPN thông qua X-UI hoặc 3X-UI panel.

## ✨ Tính năng

- ✅ **Tích hợp X-UI và 3X-UI**: Hỗ trợ cả hai loại panel phổ biến
- ✅ **Đăng ký tự động**: Tự động tạo cấu hình khi khách hàng đăng ký
- ✅ **Quản lý khách hàng**: CRUD đầy đủ cho khách hàng và subscription
- ✅ **Theo dõi traffic**: Xem thông tin sử dụng dung lượng real-time
- ✅ **Web Interface**: Giao diện web đẹp và dễ sử dụng
- ✅ **RESTful API**: API đầy đủ để tích hợp với hệ thống khác
- ✅ **Database**: Lưu trữ thông tin khách hàng và subscription

## 📋 Yêu cầu

- Python 3.8+
- X-UI hoặc 3X-UI panel đã cài đặt và chạy
- SQLite (hoặc PostgreSQL/MySQL nếu muốn)

## 🔧 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Tạo virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình

Sao chép file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
# Loại panel: xui hoặc 3xui
PANEL_TYPE=3xui

# Cấu hình 3X-UI
THREE_XUI_PANEL_URL=http://your-server-ip:2053
THREE_XUI_USERNAME=admin
THREE_XUI_PASSWORD=your-password

# Hoặc cấu hình X-UI
# XUI_PANEL_URL=http://your-server-ip:54321
# XUI_USERNAME=admin
# XUI_PASSWORD=your-password

# Cấu hình mặc định
DEFAULT_TRAFFIC_GB=100
DEFAULT_EXPIRY_DAYS=30
```

### 5. Khởi tạo database

```bash
python app.py
```

Database sẽ được tự động tạo khi chạy lần đầu.

## 🚀 Chạy ứng dụng

### Development mode

```bash
python app.py
```

Ứng dụng sẽ chạy tại: `http://localhost:5000`

### Production mode (với Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📖 Sử dụng

### Web Interface

1. **Đăng ký khách hàng mới**: Truy cập `http://localhost:5000`
   - Điền thông tin khách hàng
   - Chọn gói dịch vụ
   - Hệ thống sẽ tự động tạo cấu hình trên panel

2. **Quản lý khách hàng**: Truy cập `http://localhost:5000/dashboard`
   - Xem danh sách khách hàng
   - Xem chi tiết subscription
   - Theo dõi traffic
   - Xóa khách hàng/subscription

### REST API

#### Đăng ký khách hàng mới (Tự động tạo cấu hình)

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "name": "Nguyễn Văn A",
    "phone": "+84123456789",
    "service_name": "Standard Plan",
    "traffic_limit_gb": 100,
    "expiry_days": 30,
    "inbound_id": 1
  }'
```

#### Lấy danh sách khách hàng

```bash
curl http://localhost:5000/api/customers
```

#### Xem chi tiết khách hàng

```bash
curl http://localhost:5000/api/customers/1
```

#### Xem traffic của subscription

```bash
curl http://localhost:5000/api/subscriptions/1/traffic
```

#### Tạo subscription mới cho khách hàng có sẵn

```bash
curl -X POST http://localhost:5000/api/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "service_name": "Premium Plan",
    "traffic_limit_gb": 200,
    "expiry_days": 60,
    "inbound_id": 1
  }'
```

Xem thêm [API_DOCUMENTATION.md](API_DOCUMENTATION.md) để biết chi tiết tất cả các endpoint.

## 📁 Cấu trúc dự án

```
.
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── customer.py          # Customer model
│   │   └── subscription.py      # Subscription model
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   └── routes.py            # API endpoints
│   ├── integrations/            # Panel integrations
│   │   ├── xui_client.py        # X-UI API client
│   │   ├── three_xui_client.py  # 3X-UI API client
│   │   └── panel_manager.py     # Unified panel manager
│   ├── static/                  # Static files (CSS, JS)
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── main.js
│   │       └── dashboard.js
│   └── templates/               # HTML templates
│       ├── index.html
│       └── dashboard.html
├── app.py                       # Main application
├── config.py                    # Configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## 🔌 Tích hợp với hệ thống khác

Bạn có thể tích hợp API này với:

- **Website/Landing Page**: Gọi API `/api/register` khi khách hàng thanh toán thành công
- **Payment Gateway**: Webhook sau khi thanh toán → Tự động tạo account
- **Telegram Bot**: Bot nhận lệnh → Gọi API tạo subscription
- **WordPress/WooCommerce**: Plugin gọi API sau khi order hoàn thành

### Ví dụ tích hợp với website

```javascript
// Sau khi khách hàng thanh toán thành công
async function createVPNAccount(customerData) {
  const response = await fetch('http://your-server:5000/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: customerData.email,
      name: customerData.name,
      phone: customerData.phone,
      service_name: customerData.plan,
      traffic_limit_gb: customerData.trafficGB,
      expiry_days: customerData.days,
      inbound_id: 1
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    // Gửi email cho khách hàng với UUID và link cấu hình
    sendEmailToCustomer(result.customer, result.subscription);
  }
}
```

## 🛡️ Bảo mật

- Không commit file `.env` lên git
- Thay đổi `FLASK_SECRET_KEY` thành giá trị ngẫu nhiên
- Sử dụng HTTPS trong production
- Đặt password mạnh cho X-UI/3X-UI panel
- Cân nhắc thêm authentication cho API endpoints

## 🐛 Troubleshooting

### Không kết nối được với panel

- Kiểm tra URL panel có đúng không
- Kiểm tra username/password
- Đảm bảo panel đang chạy và có thể truy cập
- Kiểm tra firewall

### Database errors

- Xóa file `xui_manager.db` và chạy lại để tạo database mới
- Kiểm tra quyền write trong thư mục

### API không hoạt động

- Kiểm tra logs trong terminal
- Đảm bảo tất cả dependencies đã được cài đặt
- Kiểm tra port 5000 có bị chiếm bởi process khác

## 📝 License

MIT License

## 🤝 Đóng góp

Pull requests are welcome! Vui lòng mở issue trước khi làm thay đổi lớn.

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository.

---

**Lưu ý**: Hệ thống này được tạo ra để tự động hóa việc quản lý X-UI/3X-UI panel. Hãy đảm bảo bạn có quyền và tuân thủ các quy định pháp luật khi sử dụng.
