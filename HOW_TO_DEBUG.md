# 🔍 HƯỚNG DẪN DEBUG - Tìm lỗi chính xác

## 📌 Vấn đề hiện tại

User báo: **"vẫn không thể thao tác các tính năng"**

Có thể:
- ⏱️ Không gia hạn được
- 🔄 Không reset traffic được
- ⏸️/▶️ Không bật/tắt được
- ✏️ Không sửa user được

## 🔧 Đã thêm gì?

### Version v2.3.3 - Debug Mode

Tất cả các function đã được thêm debug logging:

1. **`reset_traffic()`** ✅
   - Debug payload (request data)
   - Debug response (API trả về gì)
   - Full traceback khi lỗi

2. **`extend_expiry()`** ✅
   - Debug old/new expiry time
   - Debug số ngày thay đổi
   - Debug response

3. **`toggle_inbound()`** ✅
   - Debug trạng thái enable
   - Debug response

4. **`update_inbound()`** ✅
   - Debug các thay đổi (remark, days, data)
   - Debug payload keys
   - Debug response

---

## 📋 CÁCH SỬ DỤNG DEBUG

### Bước 1: Chạy app

```bash
streamlit run vpn_admin_pro_multiserver.py
```

### Bước 2: Thử một tính năng

Ví dụ: Gia hạn user

1. Vào **👥 Quản Lý User**
2. Chọn 1 user
3. Click ⏱️ **Gia hạn**
4. Nhập số ngày → Submit

### Bước 3: Xem Debug Info

Sau khi click, sẽ thấy các **Expanders** (có thể mở):

```
🔍 Debug - Gia hạn
  Old expiry: 1732867200000
  New expiry: 1735459200000
  Diff days: 30.0

🔍 Debug Response
  Status: 200
  Response: {"success":false,"msg":"update error"}
```

**Mở các expander này để xem chi tiết!**

### Bước 4: Phân tích lỗi

#### Nếu thấy:

```json
{
  "success": false,
  "msg": "update error"
}
```

→ **API reject request** - Payload không đúng format

#### Nếu thấy:

```
Status: 401
Response: Unauthorized
```

→ **Authentication fail** - Username/password sai hoặc session hết hạn

#### Nếu thấy:

```
Status: 500
Response: Internal Server Error
```

→ **Server error** - 3X-UI panel có vấn đề

#### Nếu thấy exception:

```
❌ Update error: 'NoneType' object has no attribute 'get'
Traceback:
  File "...", line 123, in update_inbound
    ...
```

→ **Code error** - Thiếu field hoặc data structure sai

---

## 🔍 COMMON FIXES

### Fix 1: API reject "update error"

**Possible Cause:**
- Thiếu field trong payload
- Field format sai (string vs dict)
- API version khác

**Debug:**

1. Expand **🔍 Debug Info**
2. Check **Payload keys**
3. So sánh với 3X-UI original panel:
   - Mở F12 → Network
   - Thử update trên UI gốc
   - Xem request payload
   - So sánh với debug info

**Possible Solution:**

```python
# Thêm field thiếu:
payload = {
    ...existing...
    "tag": current.get('tag', 'inbound-{port}'),
    "clientStats": current.get('clientStats', ''),
}
```

### Fix 2: Authentication fail

**Solution:**

1. Vào **🔧 Quản Lý Server**
2. Click 🔍 **Test Connection** ở server đang dùng
3. Nếu fail → Click ✏️ **Edit Server**
4. Update username/password
5. Test lại

### Fix 3: Session timeout

**Solution:**

```python
# Trong login(), thêm keep-alive:
def login(host, username, password):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0',
        'Connection': 'keep-alive'
    })
    # ... rest of login
```

### Fix 4: Field format mismatch

**Debug in get_inbounds():**

```python
# Check field types
for item in inbounds:
    print(f"Settings type: {type(item['settings'])}")
    print(f"Settings value: {item['settings']}")
```

**Solution:** Ensure consistent parsing

```python
# Already done in v2.3.2
if isinstance(item['settings'], str):
    item['settings'] = json.loads(item['settings'])
```

---

## 🧪 TEST CHECKLIST

### Test 1: Reset Traffic

- [ ] Click 🔄 Reset
- [ ] Expand **🔍 Debug Info**
- [ ] Check: Request URL có đúng không?
- [ ] Check: Payload keys có đầy đủ không?
- [ ] Expand **🔍 Debug Response**
- [ ] Check: Status code = 200?
- [ ] Check: Response có "success": true?
- [ ] Result: Traffic = 0?

### Test 2: Gia hạn

- [ ] Click ⏱️ Extend
- [ ] Nhập 30 days
- [ ] Expand **🔍 Debug - Gia hạn**
- [ ] Check: Diff days = 30.0?
- [ ] Expand **🔍 Debug Response**
- [ ] Check: Status = 200, success = true?
- [ ] Result: Expiry date thay đổi?

### Test 3: Toggle

- [ ] Click ⏸️ hoặc ▶️
- [ ] Expand **🔍 Debug - Toggle**
- [ ] Check: Changing to = đúng?
- [ ] Expand response
- [ ] Check: Success?
- [ ] Result: Icon đổi màu?

### Test 4: Edit User

- [ ] Click ✏️ Edit
- [ ] Thay đổi tên/ngày/data
- [ ] Submit
- [ ] Expand **🔍 Debug - Update Inbound**
- [ ] Check: Changes hiển thị đúng?
- [ ] Expand response
- [ ] Check: Success?
- [ ] Result: Thông tin thay đổi?

---

## 📸 NẾU VẪN LỖI - REPORT GÌ?

Cần 4 thông tin:

### 1. Screenshot Debug Info

Mở expander **🔍 Debug Info** và chụp:
- Request URL
- Payload keys
- Settings type/preview

### 2. Screenshot Debug Response

Mở expander **🔍 Debug Response** và chụp:
- Status code
- Response text (có "success": true/false?)

### 3. Error Message

Nếu có error box:
- ❌ Full error text
- Traceback (nếu có)

### 4. Context

- Thao tác gì? (Reset/Extend/Toggle/Edit)
- Server nào?
- 3X-UI version?
- Protocol? (vless/vmess/trojan)

---

## 🎯 EXPECTED vs ACTUAL

### Expected (Success):

```
🔍 Debug Response
  Status: 200
  Response: {"success":true,"msg":"","obj":null}

✅ Đã cập nhật thành công!
```

### Actual (Nếu fail):

**Report chính xác:**
```
🔍 Debug Response
  Status: 200
  Response: {"success":false,"msg":"EXACT ERROR HERE"}
```

Với exact error message, có thể diagnose chính xác!

---

## 💡 DEBUGGING TIPS

### Tip 1: So sánh với UI gốc

1. Mở 3X-UI panel
2. F12 → Network tab
3. Thử operation
4. Xem request/response
5. So sánh với debug info

### Tip 2: Test từng function riêng

Không test tất cả cùng lúc. Test từng cái:
1. Reset traffic → OK? → Next
2. Toggle → OK? → Next
3. Extend → OK? → Next
4. Edit → OK? → Done

### Tip 3: Check data types

```python
# Temporary debug in code:
st.write("Type:", type(current['settings']))
st.write("Value:", current['settings'])
```

### Tip 4: Simplify payload

Nếu vẫn fail, thử payload tối giản:

```python
payload = {
    "id": inbound_id,
    "enable": True  # Only change this
}
```

Nếu OK → Dần thêm field → Tìm field nào gây lỗi

---

## 🔧 ADVANCED DEBUG

### Enable More Logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In functions:
logging.debug(f"Payload: {payload}")
logging.debug(f"Response: {resp.text}")
```

### Test API Directly:

```python
import requests

session = requests.Session()
# Login...

# Test update directly:
resp = session.post(
    "http://your-server/xui/inbound/update/123",
    data={"enable": False}
)
print(resp.status_code, resp.text)
```

### Compare with cURL:

```bash
curl -X POST "http://server/xui/inbound/update/123" \
  -H "Cookie: session=..." \
  -d "enable=false"
```

---

## ✅ SUMMARY

**Debug Mode v2.3.3 có:**

- ✅ Debug cho tất cả update functions
- ✅ Show request payload
- ✅ Show API response
- ✅ Full error traceback
- ✅ Easy-to-read expanders

**Cần làm:**

1. Run app
2. Try operation
3. Open debug expanders
4. Read error message
5. Report với screenshots

**Mục tiêu:**

→ Tìm **CHÍNH XÁC** lỗi gì  
→ Không phải đoán  
→ Debug based on facts

---

🔍 **USE DEBUG INFO - FIND REAL ISSUE!** 🔍

**Version:** v2.3.3  
**Date:** 29/11/2024  
**Status:** Debug Mode Enabled
