# 🚀 BẮT ĐẦU NGAY - ADMIN PANEL

## ✅ ĐÃ SẴN SÀNG!

Tất cả đã được cài đặt xong trên Ubuntu:
- ✅ Python 3.12.3
- ✅ Flask 3.0.0
- ✅ Tất cả dependencies
- ✅ File cấu hình (.env)
- ✅ Scripts khởi động

## 🚀 CHẠY NGAY (1 LỆNH)

```bash
cd /workspace
python3 admin_panel.py
```

Hoặc:

```bash
cd /workspace
./start.sh
```

## 🌐 TRUY CẬP

Mở browser và vào:

```
http://172.30.0.2:5000
```

**Đăng nhập:**
- Email: `admin@vpnvietnam.com`
- Password: `Vpnvietnam123@!`

## 📱 SỬ DỤNG

### 1. Dashboard
- Xem CPU, RAM, Disk, Network real-time
- Chạy Speed Test
- Xem thông tin hệ thống

### 2. Cấu hình vless
- Menu: **Cấu hình vless**
- Click **Thêm cấu hình mới**
- Điền thông tin và Lưu

### 3. Quản lý Users
- Menu: **Quản lý Users**
- Chọn Inbound
- Click **Thêm User mới**
- Xem QR Code và copy link

### 4. Monitoring VPS
- Menu: **Theo dõi VPS**
- Xem charts real-time
- Theo dõi performance

## 🛑 DỪNG SERVER

Nhấn `Ctrl + C` trong terminal

## 📚 TÀI LIỆU CHI TIẾT

- **RUN_ON_UBUNTU.md** - Hướng dẫn chạy trên Ubuntu
- **QUICKSTART.md** - Quick start guide
- **README.md** - Documentation đầy đủ
- **INSTALL.md** - Chi tiết cài đặt
- **FEATURES.md** - Danh sách tính năng

## 🔥 TIPS

### Chạy trong background:
```bash
nohup python3 admin_panel.py > log.txt 2>&1 &
```

### Xem logs:
```bash
tail -f log.txt
```

### Dừng background process:
```bash
pkill -f admin_panel.py
```

### Mở firewall (nếu cần):
```bash
sudo ufw allow 5000/tcp
```

## ✨ TÍNH NĂNG

- ✅ Dashboard tổng quan
- ✅ Speed Test Internet
- ✅ Quản lý cấu hình vless
- ✅ Quản lý Users với QR codes
- ✅ Monitoring VPS real-time
- ✅ Charts và biểu đồ
- ✅ Responsive design
- ✅ Dark theme

## 🎯 PRODUCTION

Để chạy production (24/7):

```bash
# Dùng systemd service
sudo cp admin_panel.service /etc/systemd/system/
sudo systemctl enable admin_panel
sudo systemctl start admin_panel
```

Chi tiết xem file **RUN_ON_UBUNTU.md**

---

## 🎉 ENJOY!

Admin Panel của bạn đã sẵn sàng! Happy managing! 🚀

Có câu hỏi? Đọc **README.md** hoặc **RUN_ON_UBUNTU.md**
