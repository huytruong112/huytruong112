# Hướng dẫn cài đặt chi tiết

## Phương pháp 1: Cài đặt trực tiếp trên VPS

### Bước 1: Cài đặt Python

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# CentOS/RHEL
sudo yum install python3 python3-pip -y
```

### Bước 2: Clone hoặc upload code

```bash
# Tạo thư mục
sudo mkdir -p /opt/admin_panel
cd /opt/admin_panel

# Upload code của bạn hoặc clone từ git
# git clone <your-repo> .

# Hoặc copy files
# scp -r * user@server:/opt/admin_panel/
```

### Bước 3: Tạo virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 4: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 5: Cấu hình

```bash
cp .env.example .env
nano .env
```

Chỉnh sửa thông tin:
```env
SECRET_KEY=your_random_secret_key_here
XRAY_PANEL_URL=http://your-server-ip:8001
XRAY_ADMIN_EMAIL=your_email@example.com
XRAY_ADMIN_PASSWORD=your_password
```

### Bước 6: Chạy thử

```bash
python admin_panel.py
```

Truy cập: `http://your-server-ip:5000`

### Bước 7: Cài đặt như Service (Production)

```bash
# Copy service file
sudo cp admin_panel.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable và start service
sudo systemctl enable admin_panel
sudo systemctl start admin_panel

# Check status
sudo systemctl status admin_panel

# View logs
sudo journalctl -u admin_panel -f
```

## Phương pháp 2: Cài đặt với Docker

### Bước 1: Cài đặt Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Bước 2: Cấu hình

```bash
cp .env.example .env
nano .env
```

### Bước 3: Build và chạy

```bash
# Build image
docker-compose build

# Start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Phương pháp 3: Cài đặt với Nginx Reverse Proxy

### Bước 1: Cài đặt Nginx

```bash
sudo apt install nginx -y
```

### Bước 2: Cấu hình Nginx

```bash
sudo nano /etc/nginx/sites-available/admin-panel
```

Thêm cấu hình:
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

### Bước 3: SSL với Let's Encrypt (Optional)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Phương pháp 4: Cài đặt nhanh với Script

```bash
#!/bin/bash

# Quick install script
cd /opt
git clone <your-repo> admin_panel
cd admin_panel
chmod +x run.sh
./run.sh
```

## Cấu hình Firewall

```bash
# Allow port 5000
sudo ufw allow 5000/tcp

# Or if using Nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Troubleshooting

### Port already in use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### Permission denied

```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/admin_panel
chmod +x run.sh
```

### Can't connect to 3X-UI

1. Check 3X-UI is running: `sudo systemctl status x-ui`
2. Check firewall allows connection
3. Verify credentials in .env

### Dependencies errors

```bash
# Update pip
pip install --upgrade pip

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## Bảo mật

### 1. Thay đổi Secret Key

```bash
# Generate random key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Firewall rules

```bash
# Only allow specific IPs
sudo ufw allow from YOUR_IP to any port 5000
```

### 3. SSL/TLS

Luôn sử dụng HTTPS trong production với Let's Encrypt hoặc SSL certificate.

## Cập nhật

```bash
cd /opt/admin_panel
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart admin_panel
```

## Backup

```bash
# Backup configuration
cp .env .env.backup

# Backup entire directory
tar -czf admin_panel_backup.tar.gz /opt/admin_panel
```

## Monitoring

```bash
# View logs
sudo journalctl -u admin_panel -f

# Check status
sudo systemctl status admin_panel

# Resource usage
htop
```

## Uninstall

```bash
# Stop service
sudo systemctl stop admin_panel
sudo systemctl disable admin_panel

# Remove files
sudo rm -rf /opt/admin_panel
sudo rm /etc/systemd/system/admin_panel.service

# Reload systemd
sudo systemctl daemon-reload
```

---

**Support**: Nếu gặp vấn đề, vui lòng tạo issue hoặc liên hệ support.
