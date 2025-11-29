# 🔐 SECRET PATH SUPPORT - Hướng dẫn sử dụng

## 🎯 Tính năng mới

**Version 2.0** hỗ trợ URL panel có **Secret Path** (đường dẫn bảo mật):

### Trước (v1.0):
❌ Chỉ hỗ trợ: `http://IP:PORT`

### Bây giờ (v2.0):
✅ Hỗ trợ: `http://IP:PORT`  
✅ Hỗ trợ: `http://IP:PORT/SECRET_PATH` ⭐ MỚI!

---

## 📋 Ví dụ URL hỗ trợ

### Format 1: Chuẩn (không path)
```
http://74.81.55.39:8001
https://vpn.example.com:8443
```

### Format 2: Có Secret Path ⭐
```
http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o
http://123.45.67.89:8001/my-secret-panel
https://panel.domain.com:8443/abc123xyz
```

**Giải thích:**
- `http://45.119.84.238:8888` - Base URL (IP + Port)
- `/6SnQh95LlD8LhQxQ2o` - Secret Path (đường dẫn bảo mật)

---

## 🔧 Cách hoạt động

### Khi bạn nhập URL có secret path:

**Input:**
```
http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o
```

**App sẽ tự động:**
1. **Parse URL:**
   - Base URL: `http://45.119.84.238:8888`
   - Secret Path: `/6SnQh95LlD8LhQxQ2o`

2. **Build API URLs:**
   - Login: `http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o/login`
   - List: `http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o/xui/inbound/list`
   - Add: `http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o/xui/inbound/add`
   - ...

3. **Lưu config:**
```json
{
  "server_id": {
    "name": "VPS Singapore",
    "host": "http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o",
    "base_url": "http://45.119.84.238:8888",
    "path": "/6SnQh95LlD8LhQxQ2o",
    "username": "admin",
    "password": "password"
  }
}
```

---

## 🚀 Cách sử dụng

### Bước 1: Chạy app v2
```bash
streamlit run vpn_admin_pro_multiserver_v2.py
```

### Bước 2: Thêm server
1. Vào menu **🖥️ Quản lý Server**
2. Tab **➕ Thêm Server Mới**
3. Điền thông tin:

```
Tên Server:    VPS Singapore Secret
HOST:          http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o
Username:      admin
Password:      your_password
```

4. **Preview tự động hiện:**
```
📍 Base URL: http://45.119.84.238:8888
🔐 Secret Path: /6SnQh95LlD8LhQxQ2o
```

5. Click **✅ Thêm Server**

### Bước 3: Test kết nối
- App sẽ tự động test connection
- ✅ Nếu OK → Server được thêm vào
- ❌ Nếu lỗi → Kiểm tra lại URL, username, password

### Bước 4: Sử dụng bình thường
- Switch server từ dropdown
- Tạo user, quản lý user như bình thường
- App tự động sử dụng đúng URL với secret path

---

## 🎯 So sánh v1.0 vs v2.0

| Tính năng | v1.0 | v2.0 |
|-----------|------|------|
| URL chuẩn | ✅ | ✅ |
| URL có secret path | ❌ | ✅ |
| Auto parse URL | ❌ | ✅ |
| Preview parse | ❌ | ✅ |
| Support HTTPS | ✅ | ✅ |
| Support domain | ✅ | ✅ |

---

## 💡 Use Cases

### Use Case 1: Panel bảo mật cao
**Vấn đề:**  
Panel 3X-UI của bạn public trên internet, cần ẩn đường dẫn

**Giải pháp:**  
Cấu hình panel với secret path:
```
http://your-ip:8001/very-long-random-string-abc123xyz
```

**Lợi ích:**
- ✅ Attacker không biết đường dẫn panel
- ✅ Giảm bot attack
- ✅ Tăng bảo mật

### Use Case 2: Multi-tenant
**Vấn đề:**  
Nhiều khách hàng dùng chung 1 VPS, cần tách biệt panel

**Giải pháp:**
```
Customer A: http://vps:8001/customer-a-secret
Customer B: http://vps:8001/customer-b-secret
Customer C: http://vps:8001/customer-c-secret
```

### Use Case 3: Reverse Proxy
**Vấn đề:**  
Dùng Nginx reverse proxy với custom path

**Config Nginx:**
```nginx
location /my-panel-path {
    proxy_pass http://localhost:8001;
}
```

**URL trong app:**
```
http://your-domain.com/my-panel-path
```

---

## 🔍 Debugging

### Test URL có đúng không?

**Cách 1: Test trong app**
1. Vào "Quản lý Server"
2. Thêm server (điền URL)
3. Xem preview parse → Kiểm tra Base URL và Path
4. Click "Test" để test connection

**Cách 2: Test thủ công**
```bash
# Thay URL của bạn
curl -X POST "http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o/login" \
  -d "username=admin&password=yourpass"

# Nếu thành công → Thấy response có "success"
# Nếu lỗi 404 → URL sai
```

### Lỗi thường gặp

**1. Lỗi: Connection refused**
- Kiểm tra IP, Port có đúng không
- Kiểm tra firewall
- Kiểm tra panel có chạy không

**2. Lỗi: 404 Not Found**
- Secret path sai
- Copy lại URL chính xác từ panel config

**3. Lỗi: 401 Unauthorized**
- Username hoặc password sai

**4. Lỗi: Timeout**
- Panel offline
- Network issue

---

## 📊 Technical Details

### Parse URL Function
```python
def parse_host_url(host_url):
    """
    Input:  "http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o"
    Output: ("http://45.119.84.238:8888", "/6SnQh95LlD8LhQxQ2o")
    """
    parsed = urlparse(host_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path.rstrip('/')
    return base_url, path
```

### Build API URL Function
```python
def build_api_url(base_url, path, endpoint):
    """
    Examples:
    - build_api_url("http://1.2.3.4:8001", "", "/login")
      → "http://1.2.3.4:8001/login"
    
    - build_api_url("http://1.2.3.4:8888", "/secret", "/login")
      → "http://1.2.3.4:8888/secret/login"
    """
    endpoint = endpoint.lstrip('/')
    if path:
        return f"{base_url}{path}/{endpoint}"
    else:
        return f"{base_url}/{endpoint}"
```

### Session Management
```python
session = get_session(server_config)
# Session object có attributes:
session.base_url  # "http://1.2.3.4:8888"
session.path      # "/secret" hoặc ""

# Dùng để build URL sau này:
list_url = build_api_url(session.base_url, session.path, "xui/inbound/list")
```

---

## ⚡ Migration từ v1.0 → v2.0

### Option 1: Giữ servers cũ
Servers không có secret path vẫn hoạt động bình thường:
```json
{
  "old_server": {
    "host": "http://1.2.3.4:8001",
    "username": "admin",
    ...
  }
}
```
→ App tự động parse → path = ""

### Option 2: Update servers cũ thành secret path
1. Cấu hình panel với secret path
2. Xóa server cũ trong app
3. Thêm lại với URL mới có secret path

### Option 3: Mix cả 2
- Server A: URL chuẩn
- Server B: URL có secret path
- Server C: URL chuẩn
- Server D: URL có secret path

✅ Tất cả đều hoạt động!

---

## 🔐 Security Best Practices

### 1. Dùng secret path dài và random
❌ Không tốt:
```
/admin
/panel
/123456
```

✅ Tốt:
```
/6SnQh95LlD8LhQxQ2o
/abc123xyz789RANDOM
/very-long-secret-path-12345678
```

### 2. Đổi secret path định kỳ
- Mỗi 3-6 tháng đổi 1 lần
- Update trong app

### 3. Combine với firewall
```bash
# Chỉ cho IP cố định truy cập
ufw allow from YOUR_IP to any port 8888
```

### 4. Dùng HTTPS nếu có thể
```
https://your-domain.com/secret-path
```

### 5. Don't share URL
- Secret path = password thứ 2
- Không chia sẻ public

---

## 📚 Files liên quan

- **Main app:** `vpn_admin_pro_multiserver_v2.py`
- **Old version:** `vpn_admin_pro_multiserver.py` (v1.0)
- **Fixed version:** `vpn_admin_pro_multiserver_fixed.py` (v1.1)
- **This guide:** `SECRET_PATH_GUIDE.md`

---

## ✅ Testing Checklist

### Trước khi deploy:
- [ ] Test URL chuẩn → OK
- [ ] Test URL có secret path → OK
- [ ] Test switch giữa 2 loại server → OK
- [ ] Test tạo user trên server secret path → OK
- [ ] Test tất cả functions (reset, extend, toggle) → OK
- [ ] Test preview parse URL → Chính xác
- [ ] Test backup → OK

### Production:
- [ ] Chạy app v2
- [ ] Thêm server thực
- [ ] Test connection
- [ ] Tạo 1 user test
- [ ] Verify user hoạt động
- [ ] ✅ Ready to use!

---

## 🎉 Conclusion

Version 2.0 hỗ trợ đầy đủ:
- ✅ URL chuẩn (backward compatible)
- ✅ URL có secret path (new feature)
- ✅ Auto parse và validate
- ✅ Preview trước khi add
- ✅ Tất cả tính năng v1.0

**Sẵn sàng quản lý panel bảo mật hơn! 🔐**

---

*Secret Path Support Guide*  
*Version: 2.0*  
*Date: 28/11/2024*  
*Status: Complete*
