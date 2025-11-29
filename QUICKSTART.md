# 🚀 Quick Start Guide

Bắt đầu sử dụng Admin Panel trong 5 phút!

## ⚡ Cài đặt nhanh

### Option 1: Script tự động (Khuyến nghị)

```bash
# Clone hoặc upload code vào server
cd /workspace  # hoặc thư mục của bạn

# Chạy script
chmod +x run.sh
./run.sh
```

Script sẽ tự động:
- Tạo virtual environment
- Cài đặt dependencies
- Tạo .env file
- Chạy application

### Option 2: Manual (3 bước)

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Tạo config
cp .env.example .env

# 3. Chạy
python admin_panel.py
```

### Option 3: Docker (1 lệnh)

```bash
docker-compose up -d
```

## 🔑 Đăng nhập

1. Mở browser: `http://your-server-ip:5000`
2. Login với credentials:
   - Email: `admin@vpnvietnam.com`
   - Password: `Vpnvietnam123@!`

## 📝 Cấu hình cơ bản

### File .env

```env
# Bắt buộc thay đổi
SECRET_KEY=your_random_secret_key_here

# Thông tin 3X-UI Panel (thay bằng thông tin của bạn)
XRAY_PANEL_URL=http://74.81.55.39:8001
XRAY_ADMIN_EMAIL=admin@vpnvietnam.com
XRAY_ADMIN_PASSWORD=Vpnvietnam123@!

# Optional
DEBUG=False
PORT=5000
```

### Generate Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 🎯 Sử dụng cơ bản

### 1. Xem Dashboard
- Truy cập trang chủ
- Xem system stats real-time
- Chạy speed test

### 2. Quản lý Configs
- Menu: **Cấu hình vless**
- Click **Thêm cấu hình mới**
- Điền thông tin:
  - Remark: `my-server`
  - Port: `443`
  - Network: `WebSocket`
  - Path: `/ray`
- Click **Lưu cấu hình**

### 3. Thêm User
- Menu: **Quản lý Users**
- Chọn Inbound
- Click **Thêm User mới**
- Điền thông tin:
  - Email: `user1@example.com`
  - Total GB: `50` (50GB)
  - Expiry: `30` (30 ngày)
- Click **Thêm User**

### 4. Xem QR Code
- Trong danh sách Users
- Click icon **QR Code**
- Scan hoặc copy link

### 5. Monitoring
- Menu: **Theo dõi VPS**
- Xem charts real-time
- Monitor CPU, RAM, Network

## 🔧 Troubleshooting

### Port đã được sử dụng
```bash
# Thay đổi port trong .env
PORT=8080
```

### Không kết nối được 3X-UI
```bash
# Kiểm tra 3X-UI đang chạy
curl http://your-panel-ip:8001

# Kiểm tra firewall
sudo ufw status
sudo ufw allow 8001/tcp
```

### Dependencies lỗi
```bash
# Reinstall
pip install --force-reinstall -r requirements.txt
```

## 📚 Next Steps

1. ✅ Đọc [README.md](README.md) - Full documentation
2. ✅ Đọc [INSTALL.md](INSTALL.md) - Chi tiết cài đặt
3. ✅ Đọc [FEATURES.md](FEATURES.md) - Danh sách tính năng
4. ✅ Setup SSL với Nginx (production)
5. ✅ Configure backup
6. ✅ Setup monitoring alerts

## 🎥 Video Tutorial (Coming Soon)

- [ ] Installation walkthrough
- [ ] Feature demonstration
- [ ] Configuration guide
- [ ] Troubleshooting tips

## 💡 Tips

### Performance
- Chạy trên VPS ít nhất 1GB RAM
- SSD cho database (nếu dùng)
- Enable Gzip compression với Nginx

### Security
- Luôn dùng HTTPS trong production
- Thay đổi default passwords
- Regular updates
- Backup configs thường xuyên

### Optimization
- Close unused browser tabs
- Clear cache định kỳ
- Monitor disk space
- Update dependencies

## 🆘 Support

### Common Issues

**Q: Trang không load?**
A: Kiểm tra service đang chạy: `systemctl status admin_panel`

**Q: Speed test không hoạt động?**
A: Đợi 1-2 phút, speed test cần thời gian

**Q: Charts không hiển thị?**
A: Check console browser, có thể do Chart.js CDN

**Q: Không thêm được config?**
A: Kiểm tra kết nối đến 3X-UI panel

### Get Help

1. Check [INSTALL.md](INSTALL.md) troubleshooting section
2. View logs: `sudo journalctl -u admin_panel -f`
3. Check browser console (F12)
4. Create GitHub issue

## 📱 Mobile Access

App hoạt động tốt trên mobile:
1. Mở browser trên điện thoại
2. Truy cập: `http://your-server-ip:5000`
3. Login
4. Sử dụng như bình thường

## 🌟 Pro Tips

1. **Bookmark trang** - Để truy cập nhanh
2. **Dùng HTTPS** - Với Let's Encrypt miễn phí
3. **Monitor thường xuyên** - Set reminder mỗi ngày
4. **Backup configs** - Trước khi thay đổi lớn
5. **Test trước** - Thử trên staging trước production

## 🎉 You're Ready!

Bây giờ bạn đã sẵn sàng sử dụng Admin Panel. Enjoy! 🚀

---

**Need more help?** Read the full [README.md](README.md)

**Want to customize?** Check the code comments

**Found a bug?** Create an issue

**Like the project?** Give it a star ⭐
