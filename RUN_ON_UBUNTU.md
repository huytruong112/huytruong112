# 🐧 Chạy Admin Panel trên Ubuntu

## ✅ Đã cài đặt xong!

Tất cả dependencies đã được cài đặt thành công trên Ubuntu.

## 🚀 CÁCH CHẠY

### Phương pháp 1: Chạy trực tiếp (Đơn giản nhất)

```bash
cd /workspace
python3 admin_panel.py
```

### Phương pháp 2: Dùng script

```bash
cd /workspace
./start.sh
```

### Phương pháp 3: Chạy trong background

```bash
cd /workspace
nohup python3 admin_panel.py > admin_panel.log 2>&1 &
```

## 🌐 TRUY CẬP

Sau khi chạy, truy cập admin panel tại:

```
http://YOUR_SERVER_IP:5000
```

**Thông tin đăng nhập:**
- Email: `admin@vpnvietnam.com`
- Password: `Vpnvietnam123@!`

## 📊 KIỂM TRA

### Xem log real-time:
```bash
tail -f admin_panel.log
```

### Kiểm tra process đang chạy:
```bash
ps aux | grep admin_panel
```

### Dừng server:
```bash
pkill -f admin_panel.py
```

## 🔥 Firewall (Nếu cần)

Nếu không truy cập được, mở port 5000:

```bash
# UFW
sudo ufw allow 5000/tcp
sudo ufw reload

# hoặc iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

## 🎯 PRODUCTION (Khuyến nghị)

### 1. Cài đặt như Systemd Service

```bash
# Copy service file
sudo cp admin_panel.service /etc/systemd/system/

# Chỉnh sửa đường dẫn nếu cần
sudo nano /etc/systemd/system/admin_panel.service

# Enable và start
sudo systemctl daemon-reload
sudo systemctl enable admin_panel
sudo systemctl start admin_panel

# Kiểm tra status
sudo systemctl status admin_panel

# Xem logs
sudo journalctl -u admin_panel -f
```

### 2. Với Nginx Reverse Proxy

```bash
# Cài Nginx
sudo apt install nginx -y

# Tạo config
sudo nano /etc/nginx/sites-available/admin-panel
```

Thêm nội dung:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/admin-panel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Với SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## 🔧 Troubleshooting

### Lỗi "Address already in use"

Port 5000 đã được sử dụng:
```bash
# Tìm process
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### Lỗi "Permission denied"

```bash
# Fix permissions
sudo chown -R $USER:$USER /workspace
chmod +x start.sh
```

### Lỗi import modules

```bash
# Reinstall dependencies
pip3 install --force-reinstall -r requirements.txt --user
```

## 📱 KIỂM TRA NHANH

Test xem server có chạy không:
```bash
curl http://localhost:5000
```

Nếu thấy HTML response là OK!

## 🎨 Tính năng có sẵn

✅ Dashboard với system stats real-time
✅ Speed test internet
✅ Quản lý cấu hình vless
✅ Quản lý users với QR codes
✅ Monitoring VPS với charts
✅ Settings và cấu hình

## 📞 Support

Nếu gặp vấn đề:
1. Check logs: `tail -f admin_panel.log`
2. Check process: `ps aux | grep admin_panel`
3. Check port: `sudo netstat -tulpn | grep 5000`
4. Check firewall: `sudo ufw status`

## ✨ DONE!

Admin Panel đã sẵn sàng sử dụng trên Ubuntu! 🎉

---

*Note: Đảm bảo 3X-UI Panel tại http://74.81.55.39:8001 đang hoạt động để kết nối thành công.*
