# Admin Panel cho Quản lý vless và Theo dõi VPS

Admin Panel hoàn chỉnh để quản lý cấu hình vless thông qua 3X-UI và theo dõi hệ thống VPS real-time.

## 🌟 Tính năng

### 1. Dashboard Tổng quan
- Hiển thị thống kê hệ thống real-time (CPU, RAM, Disk, Network)
- Kiểm tra tốc độ Internet (Speed Test)
- Thông tin chi tiết về server
- Thao tác nhanh

### 2. Quản lý Cấu hình vless
- Xem danh sách tất cả cấu hình inbound
- Thêm cấu hình vless mới
- Chỉnh sửa cấu hình hiện có
- Xóa cấu hình
- Bật/Tắt cấu hình
- Hỗ trợ nhiều loại network: TCP, WebSocket, gRPC
- Hỗ trợ TLS và Reality

### 3. Quản lý Users/Clients
- Thêm user mới vào inbound
- Xem danh sách users và thông tin traffic
- Giới hạn IP, Data, và thời gian sử dụng
- Tạo QR Code và link kết nối
- Theo dõi traffic của từng user

### 4. Theo dõi VPS Real-time
- CPU Usage với biểu đồ lịch sử
- Memory Usage với biểu đồ lịch sử
- Disk Usage
- Network Traffic với biểu đồ
- Thông tin Network Interfaces
- Uptime và thông tin hệ thống
- Cập nhật tự động mỗi 3-5 giây

### 5. Cài đặt
- Cấu hình kết nối 3X-UI Panel
- Tùy chỉnh monitoring settings
- System actions (Clear cache, Export config, View logs)

## 📋 Yêu cầu

- Python 3.8+
- 3X-UI Panel đã cài đặt và đang chạy
- Quyền truy cập admin vào 3X-UI Panel

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình

Tạo file `.env` từ template:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
SECRET_KEY=your_random_secret_key_here
DEBUG=False
PORT=5000

# Thông tin 3X-UI Panel
XRAY_PANEL_URL=http://your-server-ip:8001
XRAY_ADMIN_EMAIL=your_admin_email@example.com
XRAY_ADMIN_PASSWORD=your_admin_password
```

### 4. Chạy ứng dụng

```bash
python admin_panel.py
```

Hoặc sử dụng script:

```bash
chmod +x run.sh
./run.sh
```

Truy cập admin panel tại: `http://localhost:5000`

## 🔐 Đăng nhập

Sử dụng thông tin admin từ 3X-UI Panel để đăng nhập:
- Email: `admin@vpnvietnam.com`
- Password: `Vpnvietnam123@!`

## 📱 Giao diện

Admin Panel có giao diện hiện đại, responsive với:
- Dark theme chuyên nghiệp
- Animations mượt mà
- Charts và biểu đồ real-time
- Mobile-friendly
- Icons Font Awesome
- Gradient backgrounds

## 🛠️ Công nghệ sử dụng

### Backend
- **Flask** - Web framework
- **requests** - HTTP client cho 3X-UI API
- **psutil** - System monitoring
- **speedtest-cli** - Internet speed testing

### Frontend
- **HTML5** / **CSS3** / **JavaScript**
- **Chart.js** - Biểu đồ real-time
- **Font Awesome** - Icons
- **QRCode.js** - Tạo QR codes

## 📊 API Endpoints

### System
- `GET /api/system/stats` - Lấy thống kê hệ thống
- `POST /api/speed/test` - Chạy speed test
- `GET /api/speed/result` - Lấy kết quả speed test
- `GET /api/server/status` - Lấy status từ 3X-UI

### Configs
- `GET /api/configs/list` - Danh sách cấu hình
- `POST /api/configs/add` - Thêm cấu hình mới
- `POST /api/configs/update/<id>` - Cập nhật cấu hình
- `POST /api/configs/delete/<id>` - Xóa cấu hình

### Users
- `POST /api/users/add` - Thêm user mới

## 🔧 Tùy chỉnh

### Thay đổi Port

Chỉnh sửa trong `.env`:
```env
PORT=8080
```

### Thay đổi Update Interval

Chỉnh sửa trong `admin_panel.py`:
```python
updateInterval = setInterval(updateSystemStats, 5000); // 5 seconds
```

### Thêm Admin Account

Trong `admin_panel.py`, thêm logic kiểm tra nhiều admin:
```python
ADMIN_ACCOUNTS = {
    'admin@vpnvietnam.com': 'Vpnvietnam123@!',
    'admin2@example.com': 'password123'
}
```

## 🐛 Troubleshooting

### Lỗi kết nối đến 3X-UI Panel

1. Kiểm tra 3X-UI Panel đang chạy
2. Kiểm tra URL trong `.env` đúng
3. Kiểm tra firewall không block port

### Speed Test không hoạt động

Speed test có thể mất 1-2 phút để hoàn thành. Đợi và refresh kết quả.

### System Stats không cập nhật

Kiểm tra console browser để xem lỗi. Có thể do:
- Permission issues với psutil
- Background monitoring thread bị lỗi

## 📈 Performance

- System monitoring: ~5 seconds interval
- Speed test: ~30-120 seconds
- API response time: <100ms (local)
- Memory usage: ~50-100MB
- CPU usage: ~1-5% (idle)

## 🔒 Bảo mật

- Session-based authentication
- Secure password handling
- No sensitive data in frontend
- HTTPS recommended for production
- Regular security updates

## 📝 To-Do / Future Features

- [ ] Multi-user system với roles
- [ ] Database để lưu logs và history
- [ ] Email notifications
- [ ] Telegram bot integration
- [ ] Backup và restore configs
- [ ] Traffic statistics charts
- [ ] User bandwidth limits
- [ ] Automated certificate renewal
- [ ] Docker support
- [ ] Multi-server management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

VPN Vietnam Team

## 📞 Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra phần Troubleshooting
2. Xem logs trong console
3. Tạo issue trên GitHub

## 🙏 Credits

- [3X-UI](https://github.com/MHSanaei/3x-ui) - Xray management panel
- [Chart.js](https://www.chartjs.org/) - Charts library
- [Font Awesome](https://fontawesome.com/) - Icons
- [psutil](https://github.com/giampaolo/psutil) - System monitoring

---

**Note**: Admin Panel này được thiết kế để hoạt động với 3X-UI Panel. Đảm bảo bạn đã cài đặt và cấu hình 3X-UI trước khi sử dụng.
