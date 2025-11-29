# Hướng Dẫn Cài Đặt Chi Tiết

## Bước 1: Chuẩn Bị Server

### Yêu Cầu Hệ Thống
- VPS/Server với hệ điều hành Linux (Ubuntu 20.04+ hoặc CentOS 7+)
- Python 3.8 trở lên
- 1GB RAM trở lên
- x-ui hoặc 3x-ui đã được cài đặt

### Cài Đặt x-ui

```bash
bash <(curl -Ls https://raw.githubusercontent.com/dopaemon/x-ui/main/install.sh)
```

### Cài Đặt 3x-ui (Khuyến nghị)

```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

Sau khi cài đặt xong:
1. Truy cập panel qua trình duyệt: `http://your-server-ip:54321` (x-ui) hoặc `http://your-server-ip:2053` (3x-ui)
2. Đăng nhập với username/password mặc định (thường là admin/admin)
3. Đổi mật khẩu ngay lập tức
4. Tạo ít nhất 1 inbound để test

## Bước 2: Cài Đặt VPN Auto-Provisioning API

### Clone hoặc tải project

```bash
# Tạo thư mục
mkdir -p /opt/vpn-api
cd /opt/vpn-api

# Tải các file (hoặc clone từ git)
# Copy tất cả files vào thư mục này
```

### Cài đặt Python dependencies

```bash
# Cài đặt pip nếu chưa có
sudo apt update
sudo apt install python3-pip -y

# Cài đặt dependencies
pip3 install -r requirements.txt
```

## Bước 3: Cấu Hình

### Tạo file config.json

```bash
cp config.example.json config.json
nano config.json
```

Chỉnh sửa các thông tin:

```json
{
  "threexui_panels": {
    "server1": {
      "url": "http://YOUR_SERVER_IP:2053",
      "username": "your_admin_username",
      "password": "your_admin_password",
      "default_inbound_id": 1
    }
  },
  "plans": {
    "basic": {
      "panel_type": "3x-ui",
      "data_limit_gb": 50,
      "duration_days": 30,
      "protocol": "vmess",
      "network": "tcp",
      "security": "none",
      "limit_ip": 2
    },
    "premium": {
      "panel_type": "3x-ui",
      "data_limit_gb": 200,
      "duration_days": 30,
      "protocol": "vmess",
      "network": "ws",
      "security": "tls",
      "limit_ip": 5
    }
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "api_key": "CHANGE_THIS_TO_RANDOM_STRING"
  }
}
```

**Quan trọng:**
- Thay `YOUR_SERVER_IP` bằng IP thực của server
- Thay `your_admin_username` và `your_admin_password` bằng thông tin đăng nhập panel
- Thay `api_key` bằng một chuỗi ngẫu nhiên mạnh
- Kiểm tra `default_inbound_id` có tồn tại trong panel không

### Cách lấy Inbound ID

1. Đăng nhập vào 3x-ui panel
2. Vào menu "Inbounds"
3. Xem cột ID của inbound bạn muốn sử dụng
4. Điền ID đó vào `default_inbound_id`

## Bước 4: Test Kết Nối

```bash
python3 test_connection.py
```

Nếu thấy tất cả ✅ thì cấu hình đã đúng!

## Bước 5: Chạy API Server

### Chạy test (foreground)

```bash
python3 api_server.py
```

Server sẽ chạy tại `http://localhost:8000`

Kiểm tra bằng cách truy cập: `http://your-server-ip:8000/health`

### Chạy production với systemd

Tạo service file:

```bash
sudo nano /etc/systemd/system/vpn-api.service
```

Nội dung:

```ini
[Unit]
Description=VPN Auto-Provisioning API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-api
ExecStart=/usr/bin/python3 /opt/vpn-api/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Kích hoạt service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vpn-api
sudo systemctl start vpn-api
sudo systemctl status vpn-api
```

Xem logs:

```bash
sudo journalctl -u vpn-api -f
```

## Bước 6: Bảo Mật

### Cài đặt SSL với Nginx (Khuyến nghị)

```bash
# Cài đặt Nginx
sudo apt install nginx -y

# Tạo config
sudo nano /etc/nginx/sites-available/vpn-api
```

Nội dung:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Kích hoạt:

```bash
sudo ln -s /etc/nginx/sites-available/vpn-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Cài đặt SSL với Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

### Firewall

```bash
# Cho phép traffic đến API
sudo ufw allow 8000/tcp

# Hoặc nếu dùng Nginx
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Giới hạn IP truy cập (Optional)

Chỉnh sửa Nginx config để chỉ cho phép IP của web server:

```nginx
location / {
    allow YOUR_WEB_SERVER_IP;
    deny all;
    
    proxy_pass http://127.0.0.1:8000;
    ...
}
```

## Bước 7: Test API

### Test đăng ký khách hàng

```bash
curl -X POST "http://your-server-ip:8000/api/v1/customer/register" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "plan": "basic"
  }'
```

Nếu thành công, bạn sẽ thấy response:

```json
{
  "success": true,
  "message": "Đã tạo cấu hình VPN thành công",
  "data": {
    ...
  }
}
```

### Test lấy usage

```bash
curl -X POST "http://your-server-ip:8000/api/v1/customer/usage" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

## Bước 8: Tích Hợp với Website

Xem các file trong thư mục `examples/` để tích hợp với:
- PHP (WordPress, Laravel, etc.)
- Node.js (Express, NestJS, etc.)
- Python (Flask, Django, FastAPI, etc.)

## Troubleshooting

### Lỗi: Cannot connect to panel

```bash
# Kiểm tra panel có chạy không
curl http://your-server-ip:2053

# Kiểm tra firewall
sudo ufw status

# Cho phép port của panel
sudo ufw allow 2053/tcp
```

### Lỗi: Login failed

- Kiểm tra username/password có đúng không
- Đăng nhập thử vào panel qua browser
- Xem log: `sudo journalctl -u vpn-api -n 50`

### Lỗi: Inbound not found

- Kiểm tra `default_inbound_id` trong config
- Chạy `python3 test_connection.py` để xem các ID có sẵn
- Tạo inbound mới trong panel nếu chưa có

### API không response

```bash
# Kiểm tra service có chạy không
sudo systemctl status vpn-api

# Restart service
sudo systemctl restart vpn-api

# Xem log
sudo journalctl -u vpn-api -f
```

### SSL certificate issues

```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## Monitoring và Maintenance

### Xem logs

```bash
# Logs của API service
sudo journalctl -u vpn-api -f

# Logs của Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup

```bash
# Backup config
sudo cp /opt/vpn-api/config.json /opt/vpn-api/config.json.backup

# Backup toàn bộ
sudo tar -czf vpn-api-backup.tar.gz /opt/vpn-api/
```

### Update

```bash
cd /opt/vpn-api
git pull  # hoặc download files mới
sudo systemctl restart vpn-api
```

## Support

Nếu gặp vấn đề:
1. Chạy `python3 test_connection.py`
2. Xem logs: `sudo journalctl -u vpn-api -n 100`
3. Kiểm tra panel có hoạt động không
4. Kiểm tra firewall và network
