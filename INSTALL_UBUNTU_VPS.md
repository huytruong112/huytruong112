# 🚀 HƯỚNG DẪN CÀI ĐẶT TRÊN VPS UBUNTU

## 📋 Yêu cầu

- VPS Ubuntu 18.04 / 20.04 / 22.04
- RAM: Tối thiểu 512MB (Khuyến nghị 1GB+)
- Python 3.7+
- Quyền root hoặc sudo

---

## ⚡ CÀI ĐẶT TỰ ĐỘNG (KHUYẾN NGHỊ)

### Bước 1: Kết nối SSH vào VPS

```bash
ssh root@your-vps-ip
# Hoặc
ssh username@your-vps-ip
```

### Bước 2: Download & chạy script tự động

```bash
cd /root
wget https://raw.githubusercontent.com/YOUR_REPO/install_ubuntu.sh
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

**Hoặc clone repository:**

```bash
cd /root
git clone https://github.com/YOUR_REPO/vless-config-manager.git
cd vless-config-manager
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

**Hoặc dùng script local (đã có sẵn):**

```bash
cd /workspace
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

Script sẽ tự động:
- ✅ Update system
- ✅ Cài đặt Python 3
- ✅ Cài đặt pip
- ✅ Cài đặt dependencies
- ✅ Tạo systemd service
- ✅ Cấu hình firewall
- ✅ Start app

### Bước 3: Truy cập app

```
http://YOUR_VPS_IP:8501
```

---

## 🔧 CÀI ĐẶT THỦ CÔNG

### Bước 1: Update system

```bash
sudo apt update
sudo apt upgrade -y
```

### Bước 2: Cài đặt Python & pip

```bash
# Cài Python 3
sudo apt install python3 python3-pip -y

# Kiểm tra version
python3 --version
pip3 --version
```

### Bước 3: Cài đặt dependencies

```bash
pip3 install streamlit requests pandas qrcode pillow
```

### Bước 4: Download code

**Option 1: Git clone**
```bash
cd /root
git clone https://github.com/YOUR_REPO/vless-config-manager.git
cd vless-config-manager
```

**Option 2: Upload files**
```bash
# Trên máy local:
scp vless_config_manager.py root@your-vps-ip:/root/
scp run_config_manager.sh root@your-vps-ip:/root/
```

**Option 3: Tạo file trực tiếp**
```bash
cd /root
nano vless_config_manager.py
# Copy paste code từ file vless_config_manager.py
```

### Bước 5: Cấp quyền thực thi

```bash
chmod +x run_config_manager.sh
```

### Bước 6: Chạy app

```bash
./run_config_manager.sh
```

### Bước 7: Truy cập

Mở browser và truy cập:
```
http://YOUR_VPS_IP:8501
```

---

## 🔐 CẤU HÌNH FIREWALL

### Mở port 8501

**UFW (Ubuntu Firewall):**
```bash
sudo ufw allow 8501/tcp
sudo ufw reload
sudo ufw status
```

**iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
sudo iptables-save
```

**Firewall Cloud Provider:**
- AWS: Security Groups
- Google Cloud: Firewall Rules
- DigitalOcean: Firewall
- Vultr: Firewall

→ Mở port 8501 TCP

---

## 🌐 TRUY CẬP TỪ XA

### Cách 1: Truy cập trực tiếp (Đơn giản)

```
http://YOUR_VPS_IP:8501
```

**Pros:**
- Dễ dàng
- Nhanh

**Cons:**
- Không có HTTPS
- Không có domain

---

### Cách 2: SSH Tunnel (Bảo mật)

**Trên máy local:**
```bash
ssh -L 8501:localhost:8501 root@your-vps-ip
```

**Truy cập:**
```
http://localhost:8501
```

**Pros:**
- Bảo mật qua SSH
- Không cần mở port

**Cons:**
- Cần SSH connection

---

### Cách 3: Nginx Reverse Proxy (Production)

**Cài Nginx:**
```bash
sudo apt install nginx -y
```

**Cấu hình:**
```bash
sudo nano /etc/nginx/sites-available/vless-manager
```

**Nội dung:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/vless-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Truy cập:**
```
http://your-domain.com
```

**Thêm HTTPS với Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔄 CHẠY APP NHÀ NỀN (SYSTEMD SERVICE)

### Tạo service file

```bash
sudo nano /etc/systemd/system/vless-manager.service
```

**Nội dung:**
```ini
[Unit]
Description=VLESS Config Manager
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vless-config-manager
ExecStart=/usr/local/bin/streamlit run vless_config_manager.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable & start service

```bash
sudo systemctl daemon-reload
sudo systemctl enable vless-manager
sudo systemctl start vless-manager
```

### Kiểm tra status

```bash
sudo systemctl status vless-manager
```

### Quản lý service

```bash
# Start
sudo systemctl start vless-manager

# Stop
sudo systemctl stop vless-manager

# Restart
sudo systemctl restart vless-manager

# View logs
sudo journalctl -u vless-manager -f
```

---

## 📱 CHẠY SCREEN/TMUX (TẠM THỜI)

### Screen

```bash
# Cài screen
sudo apt install screen -y

# Tạo session
screen -S vless

# Chạy app
cd /root/vless-config-manager
./run_config_manager.sh

# Detach: Ctrl+A, D

# Reattach
screen -r vless

# List sessions
screen -ls

# Kill session
screen -X -S vless quit
```

### Tmux

```bash
# Cài tmux
sudo apt install tmux -y

# Tạo session
tmux new -s vless

# Chạy app
cd /root/vless-config-manager
./run_config_manager.sh

# Detach: Ctrl+B, D

# Reattach
tmux attach -t vless

# List sessions
tmux ls

# Kill session
tmux kill-session -t vless
```

---

## 🔍 KIỂM TRA APP ĐANG CHẠY

```bash
# Check port 8501
sudo netstat -tulpn | grep 8501

# Check process
ps aux | grep streamlit

# Check logs (nếu dùng systemd)
sudo journalctl -u vless-manager -n 50

# Test từ VPS
curl http://localhost:8501
```

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Command not found: streamlit"

**Fix:**
```bash
# Tìm streamlit
which streamlit

# Nếu không tìm thấy, cài lại
pip3 install --upgrade streamlit

# Hoặc dùng đường dẫn đầy đủ
/usr/local/bin/streamlit run vless_config_manager.py
```

---

### Lỗi: "Port 8501 already in use"

**Fix:**
```bash
# Tìm process đang dùng port
sudo lsof -i :8501

# Kill process
sudo kill -9 PID

# Hoặc đổi port
streamlit run vless_config_manager.py --server.port 8502
```

---

### Lỗi: "Permission denied"

**Fix:**
```bash
# Cấp quyền
chmod +x run_config_manager.sh

# Hoặc chạy với sudo
sudo ./run_config_manager.sh
```

---

### Lỗi: "Module not found"

**Fix:**
```bash
# Cài tất cả dependencies
pip3 install streamlit requests pandas qrcode pillow

# Hoặc dùng requirements.txt
pip3 install -r requirements.txt
```

---

### Không truy cập được từ bên ngoài

**Check:**

1. **Firewall VPS:**
```bash
sudo ufw status
sudo ufw allow 8501/tcp
```

2. **Firewall Cloud Provider:**
- Check Security Groups (AWS)
- Check Firewall Rules (GCP, DO, Vultr)

3. **App binding:**
```bash
# Đảm bảo app bind 0.0.0.0 (không phải 127.0.0.1)
streamlit run vless_config_manager.py --server.address 0.0.0.0
```

4. **Port listening:**
```bash
sudo netstat -tulpn | grep 8501
# Should show: 0.0.0.0:8501
```

---

## 🔐 BẢO MẬT

### 1. Đổi Port Default

```bash
streamlit run vless_config_manager.py --server.port 9999
```

### 2. Thêm Authentication (Nginx)

```nginx
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8501;
    ...
}
```

**Tạo password:**
```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

### 3. Chỉ cho phép IP cụ thể (Firewall)

```bash
# Chỉ cho phép IP của bạn
sudo ufw allow from YOUR_IP to any port 8501

# Hoặc trong Nginx
location / {
    allow YOUR_IP;
    deny all;
    ...
}
```

### 4. Sử dụng VPN/SSH Tunnel

Không mở port ra ngoài, chỉ dùng SSH tunnel.

---

## 📊 MONITORING

### Check Resource Usage

```bash
# CPU & RAM
htop

# Disk
df -h

# Network
iftop
```

### Auto-restart khi crash

Systemd service tự động restart (đã config ở trên).

---

## 🔄 UPDATE APP

```bash
# Stop app
sudo systemctl stop vless-manager

# Backup
cp vless_config_manager.py vless_config_manager.py.bak
cp vless_configs.json vless_configs.json.bak

# Update code
# (Upload file mới hoặc git pull)

# Start app
sudo systemctl start vless-manager
```

---

## 📦 BACKUP DATA

### Backup configs

```bash
# Backup file
cp vless_configs.json vless_configs.json.$(date +%Y%m%d_%H%M%S)

# Auto backup (crontab)
crontab -e

# Add:
0 2 * * * cp /root/vless-config-manager/vless_configs.json /root/backups/vless_configs.json.$(date +\%Y\%m\%d)
```

### Restore

```bash
cp vless_configs.json.20241128 vless_configs.json
sudo systemctl restart vless-manager
```

---

## ✅ CHECKLIST

- [ ] Update system
- [ ] Cài Python & pip
- [ ] Cài dependencies
- [ ] Upload/clone code
- [ ] Cấu hình firewall (port 8501)
- [ ] Chạy app
- [ ] Test truy cập: http://YOUR_VPS_IP:8501
- [ ] (Optional) Cấu hình Nginx
- [ ] (Optional) Thêm HTTPS
- [ ] (Optional) Setup systemd service
- [ ] (Optional) Backup automation

---

## 🎯 QUICK START SUMMARY

```bash
# 1. Kết nối VPS
ssh root@YOUR_VPS_IP

# 2. Update system
sudo apt update && sudo apt upgrade -y

# 3. Cài Python & dependencies
sudo apt install python3 python3-pip -y
pip3 install streamlit requests pandas qrcode pillow

# 4. Clone/upload code
cd /root
# (Upload files)

# 5. Chạy app
chmod +x run_config_manager.sh
./run_config_manager.sh

# 6. Mở firewall
sudo ufw allow 8501/tcp

# 7. Truy cập
# Browser: http://YOUR_VPS_IP:8501
```

---

## 📞 SUPPORT

**Common Issues:**
- Port not accessible → Check firewall
- Module not found → Install dependencies
- Permission denied → chmod +x script

**Logs:**
```bash
# Systemd logs
sudo journalctl -u vless-manager -f

# App output (nếu chạy manual)
# Xem output trong terminal
```

---

**🎉 DONE! App sẵn sàng trên VPS Ubuntu!**

**Truy cập:** `http://YOUR_VPS_IP:8501`

**Quản lý:** `sudo systemctl [start|stop|restart|status] vless-manager`
