# Hướng dẫn cài đặt chi tiết

## Bước 1: Cài đặt X-UI hoặc 3X-UI Panel

### Cài đặt 3X-UI (Khuyến nghị)

```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

Sau khi cài đặt:
1. Panel sẽ chạy tại: `http://your-server-ip:2053`
2. Username mặc định: `admin`
3. Password mặc định: `admin`
4. **QUAN TRỌNG**: Đổi mật khẩu ngay sau khi cài đặt!

### Hoặc cài đặt X-UI

```bash
bash <(curl -Ls https://raw.githubusercontent.com/dopaemon/x-ui/main/install.sh)
```

Panel sẽ chạy tại: `http://your-server-ip:54321`

## Bước 2: Cấu hình Panel

### Tạo Inbound mới

1. Đăng nhập vào panel web
2. Vào mục **Inbounds**
3. Click **Add Inbound**
4. Cấu hình:
   - **Protocol**: VLESS (hoặc VMess, Trojan)
   - **Port**: Chọn port (ví dụ: 443, 8443)
   - **Network**: tcp hoặc ws
   - **Security**: none hoặc tls (khuyến nghị tls cho production)
   - **Client Settings**: Có thể để trống, hệ thống sẽ tự động thêm client

5. Click **Create**

### Lấy thông tin Panel

Ghi chú lại:
- URL panel: `http://your-server-ip:port`
- Username
- Password
- Inbound ID (sẽ dùng để tự động tạo client)

## Bước 3: Cài đặt hệ thống tự động

### Trên Server (Linux/Ubuntu)

```bash
# 1. Cài đặt Python 3.8+
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 2. Clone code (hoặc upload file lên server)
mkdir vpn-auto-system
cd vpn-auto-system

# 3. Upload các file code vào thư mục này
# Hoặc sử dụng git:
# git clone <your-repo> .

# 4. Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# 5. Cài đặt dependencies
pip install -r requirements.txt

# 6. Tạo file .env
cp .env.example .env
nano .env  # Chỉnh sửa cấu hình
```

### Cấu hình file .env

```bash
nano .env
```

Nội dung:

```env
# Database - Giữ nguyên cho development
DATABASE_URL=sqlite:///./vpn_service.db

# Security - ĐỔI KEY NÀY!
SECRET_KEY=thay-bang-chuoi-random-phuc-tap

# 3X-UI Panel
XUI_2_URL=http://your-server-ip:2053
XUI_2_USERNAME=admin
XUI_2_PASSWORD=your-password-here
XUI_2_ENABLED=true

# Nếu bạn cũng có X-UI panel
XUI_1_URL=http://another-server-ip:54321
XUI_1_USERNAME=admin
XUI_1_PASSWORD=your-password-here
XUI_1_ENABLED=false

# Cấu hình dịch vụ mặc định
DEFAULT_TRAFFIC_LIMIT_GB=50
DEFAULT_EXPIRY_DAYS=30
```

**Lưu ý**: Để tạo SECRET_KEY ngẫu nhiên:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Bước 4: Chạy thử

```bash
# Kích hoạt môi trường ảo
source venv/bin/activate

# Chạy server
python main.py
```

Hoặc:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://your-server-ip:8000`

### Test API

```bash
# Kiểm tra health
curl http://localhost:8000/health

# Kiểm tra panels
curl http://localhost:8000/panels

# Đăng ký thử
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "traffic_limit_gb": 50,
    "service_duration_days": 30
  }'
```

## Bước 5: Chạy như Service (Production)

### Tạo systemd service

```bash
sudo nano /etc/systemd/system/vpn-auto.service
```

Nội dung:

```ini
[Unit]
Description=VPN Auto Provisioning Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vpn-auto-system
Environment="PATH=/root/vpn-auto-system/venv/bin"
ExecStart=/root/vpn-auto-system/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Khởi động service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vpn-auto
sudo systemctl start vpn-auto
sudo systemctl status vpn-auto
```

### Xem logs

```bash
sudo journalctl -u vpn-auto -f
```

## Bước 6: Cấu hình Nginx (Khuyến nghị)

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/vpn-api
```

Nội dung:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Kích hoạt:

```bash
sudo ln -s /etc/nginx/sites-available/vpn-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Cài đặt SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

## Bước 7: Tích hợp với Website

### Ví dụ đơn giản - Form HTML

Tạo file `register.html`:

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đăng ký VPN</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        textarea {
            width: 100%;
            height: 100px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Đăng ký dịch vụ VPN</h1>
    
    <form id="registerForm">
        <div class="form-group">
            <label>Email *</label>
            <input type="email" id="email" required>
        </div>
        
        <div class="form-group">
            <label>Tên đăng nhập *</label>
            <input type="text" id="username" required>
        </div>
        
        <div class="form-group">
            <label>Mật khẩu *</label>
            <input type="password" id="password" required minlength="6">
        </div>
        
        <div class="form-group">
            <label>Họ tên</label>
            <input type="text" id="full_name">
        </div>
        
        <div class="form-group">
            <label>Số điện thoại</label>
            <input type="tel" id="phone">
        </div>
        
        <div class="form-group">
            <label>Gói dung lượng</label>
            <select id="traffic_limit_gb">
                <option value="30">30 GB - 100.000đ/tháng</option>
                <option value="50" selected>50 GB - 150.000đ/tháng</option>
                <option value="100">100 GB - 250.000đ/tháng</option>
                <option value="200">200 GB - 400.000đ/tháng</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>Thời hạn sử dụng</label>
            <select id="service_duration_days">
                <option value="30" selected>1 tháng</option>
                <option value="60">2 tháng</option>
                <option value="90">3 tháng</option>
                <option value="180">6 tháng</option>
            </select>
        </div>
        
        <button type="submit">Đăng ký ngay</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        const API_URL = 'http://localhost:8000';  // Thay bằng URL API của bạn
        
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p>Đang xử lý...</p>';
            
            const data = {
                email: document.getElementById('email').value,
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                full_name: document.getElementById('full_name').value,
                phone: document.getElementById('phone').value,
                traffic_limit_gb: parseInt(document.getElementById('traffic_limit_gb').value),
                service_duration_days: parseInt(document.getElementById('service_duration_days').value)
            };
            
            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h2>✅ Đăng ký thành công!</h2>
                        <p><strong>Username:</strong> ${result.customer.username}</p>
                        <p><strong>Email:</strong> ${result.customer.email}</p>
                        
                        <h3>📱 Thông tin kết nối VPN:</h3>
                        <p><strong>Giao thức:</strong> ${result.vpn_config.protocol.toUpperCase()}</p>
                        <p><strong>Dung lượng:</strong> ${result.vpn_config.traffic_limit_gb} GB</p>
                        <p><strong>Hết hạn:</strong> ${new Date(result.vpn_config.expires_at).toLocaleDateString('vi-VN')}</p>
                        
                        <p><strong>Connection URL:</strong></p>
                        <textarea readonly>${result.vpn_config.connection_url}</textarea>
                        
                        <p style="margin-top: 15px; color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px;">
                            ⚠️ Vui lòng sao chép và lưu lại thông tin trên. 
                            Bạn có thể sử dụng app như V2rayNG (Android) hoặc V2rayU (iOS) để kết nối.
                        </p>
                    `;
                    
                    // Reset form
                    document.getElementById('registerForm').reset();
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>❌ Đăng ký thất bại</h3>
                        <p>${result.detail || 'Đã xảy ra lỗi, vui lòng thử lại.'}</p>
                    `;
                }
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `
                    <h3>❌ Lỗi kết nối</h3>
                    <p>${error.message}</p>
                    <p>Vui lòng kiểm tra kết nối internet và thử lại.</p>
                `;
            }
        });
    </script>
</body>
</html>
```

### Test form

```bash
# Chạy HTTP server đơn giản để test
python3 -m http.server 8080
```

Truy cập: `http://localhost:8080/register.html`

## Khắc phục sự cố

### Lỗi: "Failed to login to panel"

- Kiểm tra URL, username, password trong `.env`
- Kiểm tra panel có đang chạy không
- Kiểm tra firewall

### Lỗi: "No inbounds available"

- Đăng nhập panel và tạo ít nhất 1 inbound
- Đảm bảo inbound được enable

### Lỗi: Database

```bash
# Xóa và tạo lại database
rm vpn_service.db
python main.py
```

### Không thể kết nối từ bên ngoài

```bash
# Mở port 8000
sudo ufw allow 8000
```

## Bảo mật Production

1. **Đổi tất cả password mặc định**
2. **Sử dụng HTTPS/SSL**
3. **Giới hạn rate limit**
4. **Backup database định kỳ**
5. **Cập nhật thường xuyên**

## Liên hệ & Hỗ trợ

Nếu cần hỗ trợ, vui lòng tạo issue trên GitHub.
