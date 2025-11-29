# 📦 Hướng dẫn cài đặt chi tiết

## Cài đặt cơ bản (Recommended)

### Bước 1: Cài đặt Node.js

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

### Bước 2: Clone source code

```bash
cd /opt
git clone <repository-url> 3x-ui-service-manager
cd 3x-ui-service-manager
```

### Bước 3: Cài đặt dependencies

```bash
npm install
```

### Bước 4: Cấu hình

```bash
# Copy file .env
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

Cập nhật các thông tin:

```env
X3UI_PANEL_URL=http://your-server-ip:2053
X3UI_USERNAME=admin
X3UI_PASSWORD=your-password
JWT_SECRET=$(openssl rand -base64 32)
DEFAULT_INBOUND_ID=1
```

### Bước 5: Chạy setup

```bash
npm run setup
```

Script sẽ kiểm tra:
- ✅ File .env đã được cấu hình
- ✅ Kết nối đến 3X-UI panel
- ✅ Inbound ID hợp lệ
- ✅ Database được khởi tạo

### Bước 6: Khởi động server

```bash
npm start
```

## Cài đặt với PM2 (Production)

### Bước 1-5: Giống như trên

### Bước 6: Cài đặt PM2

```bash
npm install -g pm2
```

### Bước 7: Khởi động với PM2

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Quản lý với PM2:

```bash
# Xem logs
pm2 logs

# Restart
pm2 restart 3x-ui-service-manager

# Stop
pm2 stop 3x-ui-service-manager

# Xem status
pm2 status
```

## Cài đặt với Docker

### Bước 1: Chuẩn bị file .env

```bash
cp .env.example .env
nano .env
```

### Bước 2: Build và chạy

```bash
# Sử dụng docker-compose
docker-compose up -d

# Hoặc build thủ công
docker build -t 3x-ui-service .
docker run -d \
  --name 3x-ui-service \
  -p 3000:3000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  3x-ui-service
```

### Quản lý Docker:

```bash
# Xem logs
docker logs -f 3x-ui-service

# Restart
docker restart 3x-ui-service

# Stop
docker stop 3x-ui-service
```

## Cấu hình Nginx Reverse Proxy

### Cài đặt Nginx

```bash
sudo apt-get install nginx
```

### Tạo file cấu hình

```bash
sudo nano /etc/nginx/sites-available/3x-ui-service
```

Nội dung:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Enable site

```bash
sudo ln -s /etc/nginx/sites-available/3x-ui-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Cài đặt SSL với Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Cấu hình Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 3000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Bảo mật 3X-UI Panel

Để tăng bảo mật, chỉ cho phép truy cập 3X-UI từ localhost:

```bash
# Chỉnh sửa cấu hình 3X-UI để chỉ listen trên 127.0.0.1
# Hoặc dùng firewall chặn port 2053 từ bên ngoài

# UFW
sudo ufw deny 2053/tcp

# Firewalld
sudo firewall-cmd --permanent --remove-port=2053/tcp
sudo firewall-cmd --reload
```

## Backup và Restore

### Backup

```bash
# Backup database
cp database.sqlite database.backup.sqlite

# Backup toàn bộ
tar -czf backup-$(date +%Y%m%d).tar.gz database.sqlite .env

# Backup tự động với cron
echo "0 2 * * * cd /opt/3x-ui-service-manager && tar -czf /backup/3x-ui-$(date +\%Y\%m\%d).tar.gz database.sqlite .env" | crontab -
```

### Restore

```bash
# Restore database
cp database.backup.sqlite database.sqlite

# Restore từ tar
tar -xzf backup-20231129.tar.gz
```

## Monitoring và Logs

### Xem logs

```bash
# Nếu chạy với npm
npm start

# Nếu chạy với PM2
pm2 logs

# Nếu chạy với Docker
docker logs -f 3x-ui-service
```

### Tạo thư mục logs

```bash
mkdir -p logs
```

## Update hệ thống

```bash
# Pull code mới
git pull

# Cài đặt dependencies mới (nếu có)
npm install

# Restart service
pm2 restart 3x-ui-service-manager
# hoặc
docker-compose restart
```

## Kiểm tra kết nối 3X-UI

```bash
# Test kết nối
curl -X POST http://your-server:2053/login \
  -d "username=admin&password=admin" \
  -v

# Kiểm tra inbound
node -e "
const x3ui = require('./services/x3ui');
x3ui.login().then(() => {
  return x3ui.getInbound(1);
}).then(inbound => {
  console.log('Inbound:', inbound);
}).catch(err => {
  console.error('Error:', err);
});
"
```

## Troubleshooting

### Port đã được sử dụng

```bash
# Kiểm tra port 3000
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>
```

### Database bị lỗi

```bash
# Backup database cũ
mv database.sqlite database.old.sqlite

# Chạy lại setup
npm run setup
```

### 3X-UI không kết nối được

1. Kiểm tra 3X-UI đang chạy:
```bash
systemctl status x-ui
```

2. Kiểm tra port 2053:
```bash
sudo netstat -tulpn | grep 2053
```

3. Test kết nối:
```bash
curl http://localhost:2053
```

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs
2. Chạy `npm run setup` để kiểm tra cấu hình
3. Tạo issue trên GitHub với thông tin lỗi chi tiết
