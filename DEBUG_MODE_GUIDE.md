# 🔍 DEBUG MODE - Hướng dẫn tìm lỗi

## 🎯 Mục đích

Thêm debug logging chi tiết để xem **chính xác** lỗi gì đang xảy ra khi:
- Gia hạn không được
- Bật/Tắt không được
- Reset traffic không được
- Sửa user không được

## 🔧 Debug Features Added

### 1. Debug Info Expanders

Khi thao tác, sẽ thấy các expandable sections:

```
🔍 Debug Info
  ├─ Request URL: http://...
  ├─ Payload keys: ['up', 'down', 'total', ...]
  ├─ Settings type: <class 'str'>
  └─ Settings preview: {"clients":...

🔍 Debug Response
  ├─ Status Code: 200
  └─ Response Text: {"success":true,"msg":...
```

### 2. Error Messages Enhanced

Trước:
```
❌ Lỗi
```

Sau:
```
❌ API trả về: {"success":false,"msg":"error message"}
❌ HTTP Error 500
❌ Traceback: ...full error stack...
```

### 3. All Functions Have Debug

- ✅ `reset_traffic()` - Debug payload + response
- ✅ `extend_expiry()` - Debug old/new expiry + response
- ✅ `toggle_inbound()` - Debug enable status + response
- ✅ `update_inbound()` - (Will add if needed)

---

## 📋 How to Debug

### Step 1: Try Operation

Ví dụ: Click ⏱️ Gia hạn

### Step 2: Check Debug Info

Sẽ thấy expandable sections:

```
🔍 Debug - Gia hạn
  Old expiry: 1732867200000
  New expiry: 1735459200000
  Diff days: 30.0

🔍 Debug Response
  Status: 200
  Response: {"success":false,"msg":"update error"}
```

### Step 3: Analyze

**Nếu Status = 200 nhưng success = false:**
- API reject request
- Check "msg" field để biết lỗi gì

**Nếu Status != 200:**
- HTTP error
- Server issue hoặc auth fail

**Nếu có Exception:**
- Code error
- Xem full traceback

---

## 🔍 Common Issues & Solutions

### Issue 1: "update error" in response

**Cause:** API không chấp nhận payload

**Check:**
1. Xem Debug Info → Payload keys
2. Có thiếu field nào không?
3. Settings có đúng format không?

**Solution:**
```python
# Có thể cần thêm field:
payload = {
    ...existing fields...
    "tag": target.get('tag', ''),
    "client": target.get('client', ''),
}
```

### Issue 2: HTTP 401/403

**Cause:** Authentication fail

**Solution:**
1. Test connection ở "Quản Lý Server" → Click 🔍
2. Verify username/password
3. Re-add server nếu cần

### Issue 3: HTTP 500

**Cause:** Server error

**Solution:**
1. Check 3X-UI panel có online không?
2. Check logs trên server
3. Có thể panel đang update?

### Issue 4: "Không tìm thấy inbound"

**Cause:** Inbound ID không match

**Solution:**
1. Refresh page (F5)
2. Reload inbound list
3. Check ID có đúng không

---

## 🧪 Test Với Debug

### Test Reset Traffic:

```
1. Click 🔄 ở user bất kỳ
2. Expand "🔍 Debug Info"
   → Check: URL, Payload keys, Settings type
3. Expand "🔍 Debug Response"
   → Check: Status code, Response text
4. Nếu fail:
   → Screenshot debug info
   → Report với full error
```

### Test Gia hạn:

```
1. Click ⏱️
2. Expand "🔍 Debug - Gia hạn"
   → Verify: Old vs New expiry
   → Check: Diff = 30 days?
3. Expand "🔍 Debug Response"
   → Check response
4. If fail → Screenshot
```

### Test Toggle:

```
1. Click ⏸️ hoặc ▶️
2. Expand "🔍 Debug - Toggle"
   → Check: Current vs Target enable
3. Expand response
4. If fail → Screenshot
```

---

## 📸 What to Report

Nếu vẫn lỗi, cần report:

1. **Debug Info screenshot:**
   - Request URL
   - Payload keys
   - Settings preview

2. **Debug Response screenshot:**
   - Status code
   - Response text

3. **Error message:**
   - Full error text
   - Traceback if any

4. **Context:**
   - Which operation? (Reset/Extend/Toggle/Edit)
   - Which server?
   - 3X-UI version?

---

## 🎯 Expected Behavior

### Successful Operation:

```
🔍 Debug Response
  Status: 200
  Response: {"success":true,"msg":"","obj":null}

✅ Đã gia hạn! (hoặc tương tự)
```

### Failed Operation:

```
🔍 Debug Response
  Status: 200
  Response: {"success":false,"msg":"specific error"}

❌ API: {"success":false,"msg":"specific error"}
```

### HTTP Error:

```
🔍 Debug Response
  Status: 401
  Response: Unauthorized

❌ HTTP 401
```

---

## 💡 Tips

1. **Always check Debug Info first**
   - Giúp hiểu chính xác request gửi đi như thế nào

2. **Check Response**
   - API có nhận request không?
   - Success = true/false?
   - Error message là gì?

3. **Compare with Working UI**
   - Mở 3X-UI gốc
   - Thử operation đó
   - F12 → Network → Xem request/response
   - So sánh với debug info của mình

4. **Test on Original UI First**
   - Nếu operation fail trên UI gốc → Server issue
   - Nếu OK trên UI gốc nhưng fail ở đây → Code issue

---

## 🔧 Next Steps (If Still Fail)

1. **Collect Full Debug Info**
2. **Test on Original 3X-UI**
3. **Compare Payloads**
4. **Check API Version**
5. **Report với screenshots**

Với debug mode này, chúng ta có thể:
- ✅ Xem chính xác request gửi đi
- ✅ Xem response trả về
- ✅ Trace full error
- ✅ Diagnose chính xác vấn đề

---

**Version:** v2.3.3 - Debug Mode  
**Date:** 29/11/2024  
**Purpose:** Diagnostic & Troubleshooting

🔍 **USE DEBUG INFO TO FIND THE REAL ISSUE!** 🔍
