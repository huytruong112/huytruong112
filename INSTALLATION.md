# 📦 Hướng dẫn cài đặt chi tiết

Tài liệu này hướng dẫn chi tiết cách cài đặt và cấu hình hệ thống quản lý X-UI/3X-UI.

## Yêu cầu hệ thống

### Server yêu cầu

- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: Tối thiểu 512MB (Khuyến nghị 1GB+)
- **CPU**: 1 core trở lên
- **Storage**: 5GB trở lên
- **Python**: 3.8 trở lên

### Phần mềm cần thiết

- Python 3.8+
- pip (Python package manager)
- virtualenv (khuyến nghị)
- X-UI hoặc 3X-UI panel đã cài đặt

## Bước 1: Cài đặt X-UI hoặc 3X-UI

### Cài đặt 3X-UI (Khuyến nghị)

```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

Sau khi cài đặt:
1. Đăng nhập vào panel: `http://your-server-ip:2053`
2. Username/Password mặc định: `admin/admin` (Nên đổi ngay)
3. Tạo ít nhất 1 inbound (VLESS hoặc VMess)

### Cài đặt X-UI (Thay thế)

```bash
bash <(curl -Ls https://raw.githubusercontent.com/dopaemon/x-ui/main/install.sh)
```

Sau khi cài đặt:
1. Đăng nhập vào panel: `http://your-server-ip:54321`
2. Username/Password mặc định: `admin/admin` (Nên đổi ngay)
3. Tạo ít nhất 1 inbound

## Bước 2: Cài đặt Python và dependencies

### Ubuntu/Debian

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Cài đặt Python và pip
sudo apt install python3 python3-pip python3-venv -y

# Kiểm tra version
python3 --version
pip3 --version
```

### CentOS/RHEL

```bash
# Update system
sudo yum update -y

# Cài đặt Python
sudo yum install python3 python3-pip -y

# Kiểm tra version
python3 --version
pip3 --version
```

## Bước 3: Clone và cài đặt ứng dụng

### 3.1. Clone repository

```bash
# Clone project
git clone <your-repository-url>
cd <project-directory>

# Hoặc tải về và giải nén
wget <download-url>
unzip <file.zip>
cd <project-directory>
```

### 3.2. Tạo virtual environment

```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate

# Verify
which python  # Should show path to venv/bin/python
```

### 3.3. Cài đặt dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Cài đặt packages
pip install -r requirements.txt

# Verify installation
pip list
```

## Bước 4: Cấu hình ứng dụng

### 4.1. Tạo file .env

```bash
# Copy file mẫu
cp .env.example .env

# Chỉnh sửa file
nano .env
```

### 4.2. Cấu hình cho 3X-UI

```env
# Database
DATABASE_URL=sqlite:///./xui_manager.db

# Flask
FLASK_SECRET_KEY=your-random-secret-key-here-change-this
FLASK_ENV=production
FLASK_DEBUG=False

# Panel Type
PANEL_TYPE=3xui

# 3X-UI Configuration
THREE_XUI_PANEL_URL=http://your-server-ip:2053
THREE_XUI_USERNAME=admin
THREE_XUI_PASSWORD=your-password

# Service Defaults
DEFAULT_TRAFFIC_GB=100
DEFAULT_EXPIRY_DAYS=30
DEFAULT_PORT=443
DEFAULT_PROTOCOL=vless
```

### 4.3. Cấu hình cho X-UI

```env
# Database
DATABASE_URL=sqlite:///./xui_manager.db

# Flask
FLASK_SECRET_KEY=your-random-secret-key-here-change-this
FLASK_ENV=production
FLASK_DEBUG=False

# Panel Type
PANEL_TYPE=xui

# X-UI Configuration
XUI_PANEL_URL=http://your-server-ip:54321
XUI_USERNAME=admin
XUI_PASSWORD=your-password

# Service Defaults
DEFAULT_TRAFFIC_GB=100
DEFAULT_EXPIRY_DAYS=30
DEFAULT_PORT=443
DEFAULT_PROTOCOL=vless
```

### 4.4. Tạo SECRET_KEY ngẫu nhiên

```bash
# Tạo secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Copy output và paste vào .env
```

## Bước 5: Kiểm tra kết nối

### 5.1. Test kết nối với panel

```bash
# Tạo file test
cat > test_connection.py << 'EOF'
from config import Config
from app.integrations.panel_manager import PanelManager

panel = PanelManager()
inbounds = panel.get_inbounds()

if inbounds:
    print("✅ Kết nối thành công!")
    print(f"Tìm thấy {len(inbounds)} inbounds:")
    for inbound in inbounds:
        print(f"  - ID: {inbound.get('id')}, Port: {inbound.get('port')}, Protocol: {inbound.get('protocol')}")
else:
    print("❌ Không thể kết nối với panel")
EOF

# Chạy test
python3 test_connection.py

# Xóa file test
rm test_connection.py
```

### 5.2. Khởi tạo database

```bash
# Chạy để tạo database
python3 app.py

# Ctrl+C để dừng sau khi thấy "Running on http://..."
```

## Bước 6: Chạy ứng dụng

### 6.1. Development mode

```bash
# Chạy development server
python3 app.py

# Ứng dụng chạy tại: http://localhost:5000
```

### 6.2. Production mode với Gunicorn

```bash
# Cài đặt Gunicorn
pip install gunicorn

# Chạy với Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Hoặc chạy trong background
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > gunicorn.log 2>&1 &
```

### 6.3. Tạo systemd service (Khuyến nghị)

```bash
# Tạo service file
sudo nano /etc/systemd/system/xui-manager.service
```

Nội dung file:

```ini
[Unit]
Description=X-UI/3X-UI Manager
After=network.target

[Service]
Type=notify
User=your-username
Group=your-username
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/venv/bin"
ExecStart=/path/to/project/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Thay thế:
- `your-username`: Username Linux của bạn
- `/path/to/project`: Đường dẫn đến thư mục project

Sau đó:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Kích hoạt service
sudo systemctl enable xui-manager

# Start service
sudo systemctl start xui-manager

# Kiểm tra status
sudo systemctl status xui-manager

# Xem logs
sudo journalctl -u xui-manager -f
```

## Bước 7: Cấu hình Nginx (Optional)

### 7.1. Cài đặt Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx -y

# CentOS
sudo yum install nginx -y
```

### 7.2. Cấu hình reverse proxy

```bash
# Tạo config
sudo nano /etc/nginx/sites-available/xui-manager
```

Nội dung:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Thay bằng domain của bạn

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Kích hoạt:

```bash
# Link config
sudo ln -s /etc/nginx/sites-available/xui-manager /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 7.3. Cài đặt SSL với Let's Encrypt

```bash
# Cài đặt Certbot
sudo apt install certbot python3-certbot-nginx -y

# Lấy SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto renewal
sudo systemctl enable certbot.timer
```

## Bước 8: Cấu hình Firewall

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 5000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Bước 9: Test hệ thống

### 9.1. Test web interface

```bash
# Mở browser và truy cập
http://your-server-ip:5000
# Hoặc
https://your-domain.com
```

### 9.2. Test API

```bash
# Health check
curl http://localhost:5000/api/health

# Register customer
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "service_name": "Basic Plan",
    "traffic_limit_gb": 100,
    "expiry_days": 30
  }'

# Get customers
curl http://localhost:5000/api/customers
```

## Backup và Restore

### Backup

```bash
# Backup database
cp xui_manager.db xui_manager.db.backup

# Backup .env
cp .env .env.backup

# Tạo tarball
tar -czf backup-$(date +%Y%m%d).tar.gz xui_manager.db .env
```

### Restore

```bash
# Extract backup
tar -xzf backup-20250101.tar.gz

# Restore database
cp xui_manager.db.backup xui_manager.db

# Restart service
sudo systemctl restart xui-manager
```

## Troubleshooting

### Không kết nối được panel

```bash
# Test kết nối
curl http://your-panel-ip:2053/login

# Kiểm tra firewall
sudo ufw status
sudo firewall-cmd --list-all

# Kiểm tra panel có chạy không
systemctl status x-ui  # hoặc 3x-ui
```

### Database errors

```bash
# Xóa và tạo lại database
rm xui_manager.db
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Port đã được sử dụng

```bash
# Tìm process đang dùng port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### Permission errors

```bash
# Sửa quyền
chmod +x app.py
chown -R your-username:your-username /path/to/project
```

## Update ứng dụng

```bash
# Dừng service
sudo systemctl stop xui-manager

# Backup
cp xui_manager.db xui_manager.db.backup

# Pull updates
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl start xui-manager
```

## Monitoring

### Xem logs

```bash
# Systemd logs
sudo journalctl -u xui-manager -f

# Application logs (nếu dùng file logging)
tail -f logs/app.log

# Gunicorn logs
tail -f gunicorn.log
```

### Giám sát resources

```bash
# CPU và RAM
htop

# Disk usage
df -h

# Kiểm tra service
systemctl status xui-manager
```

## Security Checklist

- [ ] Đổi password mặc định của X-UI/3X-UI
- [ ] Đặt SECRET_KEY mạnh và ngẫu nhiên
- [ ] Không expose database port ra ngoài
- [ ] Cài đặt SSL certificate
- [ ] Cấu hình firewall đúng cách
- [ ] Backup database định kỳ
- [ ] Update hệ thống thường xuyên
- [ ] Monitor logs để phát hiện bất thường

## Liên hệ hỗ trợ

Nếu gặp vấn đề trong quá trình cài đặt, vui lòng:
1. Kiểm tra lại các bước trong tài liệu
2. Xem logs để tìm lỗi cụ thể
3. Tạo issue trên GitHub với thông tin chi tiết

---

**Chúc bạn cài đặt thành công!** 🎉
