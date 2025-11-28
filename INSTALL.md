# 🚀 Hướng dẫn cài đặt chi tiết VPN Admin Pro

## 📋 Yêu cầu hệ thống

### Server/VPS:
- **OS:** Ubuntu 20.04+, Debian 10+, CentOS 7+
- **RAM:** Tối thiểu 512MB (khuyến nghị 1GB+)
- **CPU:** 1 core trở lên
- **Disk:** 5GB trống
- **Network:** Kết nối internet ổn định
- **3X-UI Panel:** Đã cài đặt và đang chạy

### Local Machine (để chạy dashboard):
- **Python:** 3.8 hoặc cao hơn
- **pip:** Phiên bản mới nhất
- **Browser:** Chrome, Firefox, Safari, Edge

---

## 📦 Cài đặt trên VPS

### Bước 1: Kết nối SSH
```bash
ssh root@YOUR_VPS_IP
```

### Bước 2: Cài đặt Python & pip (nếu chưa có)

**Ubuntu/Debian:**
```bash
apt update
apt install -y python3 python3-pip git
```

**CentOS:**
```bash
yum install -y python3 python3-pip git
```

### Bước 3: Clone hoặc upload code
```bash
# Option 1: Clone từ Git
git clone https://github.com/yourusername/vpn-admin-pro.git
cd vpn-admin-pro

# Option 2: Upload file thủ công
# Sử dụng SCP hoặc FTP để tải file lên
```

### Bước 4: Cài đặt dependencies
```bash
pip3 install -r requirements.txt
```

### Bước 5: Cấu hình kết nối
```bash
nano vpn_admin_pro.py
```

Tìm và sửa 3 dòng sau:
```python
HOST = "http://YOUR_VPS_IP:8001"  # IP VPS của bạn
USERNAME = "admin"                 # Username 3X-UI
PASSWORD = "your_password"         # Password 3X-UI
```

Ví dụ:
```python
HOST = "http://74.81.55.39:8001"
USERNAME = "admin"
PASSWORD = "MySecurePass123"
```

Lưu file: `Ctrl + X` → `Y` → `Enter`

### Bước 6: Mở port Streamlit (8501)
```bash
# UFW (Ubuntu/Debian)
ufw allow 8501/tcp

# Firewalld (CentOS)
firewall-cmd --permanent --add-port=8501/tcp
firewall-cmd --reload

# iptables
iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
```

### Bước 7: Chạy ứng dụng
```bash
# Chạy trực tiếp (sẽ dừng khi đóng SSH)
streamlit run vpn_admin_pro.py --server.port 8501 --server.address 0.0.0.0

# Chạy nền với nohup
nohup streamlit run vpn_admin_pro.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

### Bước 8: Truy cập Dashboard
Mở browser và truy cập:
```
http://YOUR_VPS_IP:8501
```

---

## 🖥️ Cài đặt trên Local (Windows/Mac/Linux)

### Windows:

**1. Cài Python:**
- Tải từ: https://www.python.org/downloads/
- Chạy installer, tick "Add Python to PATH"

**2. Mở Command Prompt:**
```cmd
# Kiểm tra Python
python --version

# Di chuyển đến thư mục code
cd C:\path\to\vpn-admin-pro

# Cài dependencies
pip install -r requirements.txt

# Chạy app
streamlit run vpn_admin_pro.py
```

### macOS:

**1. Cài Python (nếu chưa có):**
```bash
# Sử dụng Homebrew
brew install python3

# Hoặc tải từ python.org
```

**2. Chạy:**
```bash
cd /path/to/vpn-admin-pro
pip3 install -r requirements.txt
streamlit run vpn_admin_pro.py
```

### Linux Desktop:

```bash
# Cài Python
sudo apt install python3 python3-pip  # Ubuntu/Debian
sudo yum install python3 python3-pip  # CentOS

# Cài dependencies
cd /path/to/vpn-admin-pro
pip3 install -r requirements.txt

# Chạy
streamlit run vpn_admin_pro.py
```

---

## 🔧 Cấu hình nâng cao

### Chạy như service (systemd)

**1. Tạo file service:**
```bash
sudo nano /etc/systemd/system/vpn-admin.service
```

**2. Nội dung:**
```ini
[Unit]
Description=VPN Admin Pro Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vpn-admin-pro
ExecStart=/usr/local/bin/streamlit run vpn_admin_pro.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Kích hoạt service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable vpn-admin.service
sudo systemctl start vpn-admin.service

# Kiểm tra trạng thái
sudo systemctl status vpn-admin.service

# Xem log
sudo journalctl -u vpn-admin.service -f
```

### Sử dụng Nginx Reverse Proxy

**1. Cài Nginx:**
```bash
sudo apt install nginx
```

**2. Cấu hình:**
```bash
sudo nano /etc/nginx/sites-available/vpn-admin
```

```nginx
server {
    listen 80;
    server_name vpnadmin.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**3. Kích hoạt:**
```bash
sudo ln -s /etc/nginx/sites-available/vpn-admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL với Let's Encrypt

```bash
# Cài certbot
sudo apt install certbot python3-certbot-nginx

# Lấy certificate
sudo certbot --nginx -d vpnadmin.yourdomain.com

# Auto-renew
sudo certbot renew --dry-run
```

---

## 🔐 Bảo mật

### 1. Thay đổi password Panel
```bash
# Login vào 3X-UI Panel
# Settings → Change Password
```

### 2. Firewall rules
```bash
# Chỉ cho phép IP cụ thể truy cập Dashboard
ufw allow from YOUR_IP to any port 8501

# Deny tất cả các IP khác
ufw deny 8501
```

### 3. SSH Key Authentication
```bash
# Tạo SSH key trên local
ssh-keygen -t rsa -b 4096

# Copy public key lên server
ssh-copy-id root@YOUR_VPS_IP

# Disable password login
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart sshd
```

### 4. Fail2ban (chống brute-force)
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🐛 Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'streamlit'"
```bash
# Cài lại dependencies
pip3 install -r requirements.txt --upgrade
```

### Lỗi: "Connection refused" khi truy cập
```bash
# Kiểm tra app có chạy không
ps aux | grep streamlit

# Kiểm tra port
netstat -tuln | grep 8501

# Kiểm tra firewall
ufw status
```

### Lỗi: "❌ Mất kết nối tới Panel"
```bash
# Kiểm tra 3X-UI có chạy không
systemctl status x-ui

# Test API thủ công
curl -X POST http://YOUR_IP:8001/login \
  -d "username=admin&password=yourpass"

# Kiểm tra HOST trong code
nano vpn_admin_pro.py
# Đảm bảo HOST = "http://IP:PORT" đúng
```

### Lỗi: "Port 8501 already in use"
```bash
# Tìm process đang dùng port
lsof -i :8501

# Kill process
kill -9 PID

# Hoặc dùng port khác
streamlit run vpn_admin_pro.py --server.port 8502
```

### App chạy chậm
```bash
# Tăng resources cho VPS
# Hoặc tối ưu database 3X-UI

# Clear cache
# Vào menu Hệ Thống → Làm mới Cache
```

---

## 📊 Kiểm tra sau cài đặt

### Checklist:
- [ ] Python 3.8+ đã cài
- [ ] Dependencies đã install
- [ ] HOST, USERNAME, PASSWORD đã cấu hình đúng
- [ ] 3X-UI Panel đang chạy
- [ ] Port 8501 đã mở
- [ ] Streamlit app đang chạy
- [ ] Truy cập được qua browser
- [ ] Kết nối API thành công (không hiện lỗi đỏ)
- [ ] Có thể tạo user test

### Test cơ bản:
1. Truy cập Dashboard → Xem metrics
2. Tạo 1 user test
3. Xem danh sách user
4. Xem link + QR code
5. Reset traffic
6. Xóa user test

---

## 📝 Log Files

### Xem log Streamlit:
```bash
# Nếu chạy với nohup
tail -f streamlit.log

# Nếu chạy với systemd
sudo journalctl -u vpn-admin.service -f
```

### Xem log 3X-UI:
```bash
# Thường ở
/var/log/x-ui/x-ui.log
```

---

## 🔄 Update

### Cập nhật code mới:
```bash
cd /root/vpn-admin-pro
git pull origin main

# Hoặc upload file mới thủ công

# Cài dependencies mới (nếu có)
pip3 install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart vpn-admin.service
```

---

## 📞 Support

- **Issues:** Tạo issue trên GitHub
- **Docs:** Xem README.md và FEATURES.md
- **Telegram:** @vpnadminpro

---

## ✅ Installation Complete!

Nếu mọi thứ hoạt động, bạn đã có:
- ✅ Dashboard quản lý VPN đầy đủ chức năng
- ✅ Tạo user tự động với link + QR
- ✅ Quản lý: Reset, Gia hạn, Bật/Tắt, Xóa
- ✅ Backup dữ liệu
- ✅ Giám sát tài nguyên
- ✅ Thống kê chi tiết

**Enjoy! 🎉**
