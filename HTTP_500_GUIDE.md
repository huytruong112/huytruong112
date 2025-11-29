# 🔧 HTTP 500 ERROR - Hướng dẫn sửa

## 🎯 Vấn đề

Debug shows:
```
Old expiry: 1769567469482
New expiry: 1772159469482
Diff days: 30.0

Status: 500
Response: (empty or error)

❌ HTTP 500
```

**HTTP 500 = Internal Server Error** từ 3X-UI API

## 🔍 Nguyên nhân có thể

### 1. Thiếu field bắt buộc

3X-UI có thể yêu cầu thêm fields như:
- `tag`
- `clientStats`
- `inboundId`
- etc.

### 2. Field format sai

Có thể:
- `settings` phải là string hoặc dict?
- `streamSettings` phải là string hoặc dict?
- `sniffing` phải là string hoặc dict?

### 3. 3X-UI version khác

API endpoints/formats có thể khác giữa các versions

### 4. Server thật sự lỗi

3X-UI panel có vấn đề

## 📋 CẦN LÀM NGAY

### Bước 1: Xem FULL PAYLOAD

Giờ debug sẽ show **FULL PAYLOAD** khi bạn test lại.

**Chạy lại app:**

```bash
cd /workspace
./run_app.sh
```

**Test lại gia hạn:**
1. Click ⏱️ Gia hạn
2. Nhập 30 days
3. Submit
4. **Mở expander "🔍 Debug - Gia hạn"** (giờ tự động mở)
5. **Screenshot FULL PAYLOAD section**
6. Paste vào chat!

### Bước 2: So sánh với UI gốc

**Mở 3X-UI panel gốc:**
1. Vào Inbounds
2. Edit một inbound
3. F12 → Network tab
4. Click Update
5. Xem request payload
6. So sánh với payload của mình

**SCREENSHOT request payload từ UI gốc!**

## 🔧 Possible Fixes

### Fix 1: Thêm field thiếu

Nếu UI gốc có thêm fields, cần add:

```python
payload = {
    ...existing fields...
    "tag": target.get('tag', f'inbound-{target["port"]}'),
    "clientStats": target.get('clientStats', ''),
}
```

### Fix 2: Đổi field format

Thử send as JSON string thay vì dict:

```python
# Current
"settings": json.dumps(target['settings'])

# Try
"settings": target['settings']  # Keep as is
```

### Fix 3: Use JSON payload

Thay vì `data=payload`, thử `json=payload`:

```python
resp = session.post(
    f"{host}/xui/inbound/update/{inbound_id}", 
    json=payload,  # Instead of data=payload
    timeout=10
)
```

### Fix 4: Simplify payload

Test với minimal payload:

```python
payload = {
    "id": inbound_id,
    "expiryTime": new_expiry,
    "enable": target['enable']
}
```

Nếu OK → Dần thêm fields → Tìm field nào gây lỗi

## 📸 CẦN THÔNG TIN

Để sửa chính xác, cần:

1. **Screenshot FULL PAYLOAD** từ debug expander
   - Có tất cả fields
   - Có values

2. **Screenshot payload từ 3X-UI gốc**
   - F12 → Network → Update request
   - Request Payload section

3. **3X-UI version**
   - Version bao nhiêu?

4. **Protocol**
   - vless? vmess? trojan? shadowsocks?

## 🎯 Test Case

**Để test API format, thử direct API call:**

```python
import requests
import json

# Login
session = requests.Session()
resp = session.post(
    "http://your-server:port/login",
    data={"username": "admin", "password": "pass"}
)

# Test minimal update
payload = {
    "id": 123,  # Your inbound ID
    "enable": True
}

resp = session.post(
    "http://your-server:port/xui/inbound/update/123",
    json=payload
)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
```

Nếu minimal payload OK → Dần thêm fields

## ✅ Next Steps

1. **Run app lại** (giờ có FULL PAYLOAD debug)
2. **Test gia hạn lại**
3. **Screenshot FULL PAYLOAD**
4. **Screenshot payload từ UI gốc** (F12 → Network)
5. **Paste cả 2 vào chat**

→ Với 2 payloads, tôi có thể so sánh và fix chính xác!

---

**Đang chờ:**
- Screenshot FULL PAYLOAD từ app
- Screenshot payload từ 3X-UI gốc

**Sau đó sẽ:**
- So sánh 2 payloads
- Tìm field thiếu/sai
- Fix chính xác

---

**Version:** v2.3.3  
**Status:** Debugging HTTP 500  
**Date:** 29/11/2024

🔍 **NEED FULL PAYLOAD TO FIX!** 🔍
