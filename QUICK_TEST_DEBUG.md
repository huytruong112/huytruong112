# ⚡ QUICK TEST - Debug Mode v2.3.3

## 🎯 Mục tiêu

Test ngay để xem **chính xác lỗi gì** đang xảy ra!

---

## 🚀 Quick Start (3 phút)

### Bước 1: Chạy App (30 giây)

```bash
cd /workspace
streamlit run vpn_admin_pro_multiserver.py
```

### Bước 2: Login (30 giây)

1. Chọn server từ sidebar
2. App tự login

### Bước 3: Test 1 Operation (1 phút)

Chọn 1 trong 4:

**Option A: Test Reset Traffic** 🔄

```
1. Vào: 👥 Quản Lý User
2. Tìm user bất kỳ có traffic > 0
3. Click: 🔄 (button Reset)
4. → Sẽ thấy debug expanders xuất hiện!
```

**Option B: Test Gia hạn** ⏱️

```
1. Vào: 👥 Quản Lý User
2. Tìm user bất kỳ
3. Click: ⏱️ (button Gia hạn)
4. Nhập: 30 (days)
5. Click: Submit
6. → Sẽ thấy debug expanders!
```

**Option C: Test Toggle** ⏸️/▶️

```
1. Vào: 👥 Quản Lý User
2. Tìm user bất kỳ
3. Click: ⏸️ hoặc ▶️
4. → Sẽ thấy debug expanders!
```

**Option D: Test Edit User** ✏️

```
1. Vào: 👥 Quản Lý User
2. Tìm user bất kỳ
3. Click: ✏️ (button Edit)
4. Thay đổi: Tên hoặc Ngày
5. Click: Submit
6. → Sẽ thấy debug expanders!
```

### Bước 4: Xem Debug (1 phút)

**Mở 2 expanders này:**

```
🔍 Debug Info (hoặc Debug - Gia hạn/Toggle/Update)
  ↓ Click để mở
  → Xem: Request URL, Payload, etc.

🔍 Debug Response
  ↓ Click để mở
  → Xem: Status code, Response text
```

---

## 📸 Screenshot & Report

### Nếu Operation THÀNH CÔNG:

```
✅ Đã reset traffic!
✅ Đã gia hạn!
✅ Đã toggle!
✅ Đã cập nhật!
```

→ **DONE!** Không cần report gì cả!

### Nếu Operation THẤT BẠI:

```
❌ API trả về: {...}
❌ HTTP Error 500
❌ Error: ...
```

→ **SCREENSHOT 3 thứ:**

1. **Debug Info expander** (opened)
   - Shows request details

2. **Debug Response expander** (opened)
   - Shows API response

3. **Error message** (if any)
   - Red error box

**Paste 3 screenshots vào chat!**

---

## 🔍 What to Look For

### Case 1: Success Response

```
🔍 Debug Response
  Status Code: 200
  Response Text: {"success":true,"msg":"","obj":null}

✅ Đã ... thành công!
```

→ **PERFECT!** Everything works!

### Case 2: API Reject

```
🔍 Debug Response
  Status Code: 200
  Response Text: {"success":false,"msg":"update error"}

❌ API trả về: {"success":false,"msg":"update error"}
```

→ **Issue:** API doesn't like the payload  
→ **Action:** Screenshot + report "update error"

### Case 3: Auth Fail

```
🔍 Debug Response
  Status Code: 401
  Response Text: Unauthorized

❌ HTTP Error 401
```

→ **Issue:** Authentication problem  
→ **Action:** Test connection, re-login

### Case 4: Server Error

```
🔍 Debug Response
  Status Code: 500
  Response Text: Internal Server Error

❌ HTTP Error 500
```

→ **Issue:** 3X-UI server problem  
→ **Action:** Check if panel is online

### Case 5: Exception

```
❌ Update error: 'NoneType' object has no attribute 'get'

Traceback (most recent call last):
  File "...", line 123
    ...
```

→ **Issue:** Code error  
→ **Action:** Screenshot full traceback

---

## 💡 Quick Diagnosis Table

| Debug Response | Meaning | Action |
|---------------|---------|--------|
| Status 200 + success: true | ✅ Works! | Nothing |
| Status 200 + success: false + msg | ❌ API reject | Screenshot msg |
| Status 401/403 | ❌ Auth fail | Re-login |
| Status 500 | ❌ Server error | Check panel |
| Exception + Traceback | ❌ Code error | Screenshot trace |

---

## 🎯 Expected Result

### If Working:

```bash
# Test Reset Traffic
User A: Traffic 500MB
Click 🔄
→ Debug Response: {"success":true}
→ ✅ Đã reset traffic!
→ User A: Traffic 0MB
```

### If Failing:

```bash
# Test Reset Traffic
User A: Traffic 500MB
Click 🔄
→ Debug Response: {"success":false,"msg":"error detail"}
→ ❌ API trả về: error detail
→ User A: Traffic still 500MB

→ SCREENSHOT THIS!
```

---

## 📋 Quick Test Checklist

### Test 1: Reset (30s)

- [ ] Click 🔄
- [ ] See debug expanders
- [ ] Open both expanders
- [ ] Check Status + Response
- [ ] Result: Success or Fail?
- [ ] If fail: Screenshot

### Test 2: Extend (30s)

- [ ] Click ⏱️
- [ ] Enter 30 days
- [ ] Submit
- [ ] Open debug expanders
- [ ] Check old/new expiry
- [ ] Check response
- [ ] Result: Success or Fail?
- [ ] If fail: Screenshot

### Test 3: Toggle (30s)

- [ ] Click ⏸️ or ▶️
- [ ] Open debug expanders
- [ ] Check state change
- [ ] Check response
- [ ] Result: Success or Fail?
- [ ] If fail: Screenshot

### Test 4: Edit (30s)

- [ ] Click ✏️
- [ ] Change name/days
- [ ] Submit
- [ ] Open debug expanders
- [ ] Check changes
- [ ] Check response
- [ ] Result: Success or Fail?
- [ ] If fail: Screenshot

---

## 🎬 Example Session

```
$ streamlit run vpn_admin_pro_multiserver.py

[Browser opens]

1. Sidebar: Select "Server A"
2. Menu: Click "👥 Quản Lý User"
3. User list appears
4. Find "Client ABC"
5. Click ⏱️ (Gia hạn)
6. Enter: 30
7. Click: Submit

[Page updates]

🔍 Debug - Gia hạn (collapsed) ← CLICK HERE!
  Old expiry: 1732867200000
  New expiry: 1735459200000
  Diff days: 30.0

🔍 Debug Response (collapsed) ← CLICK HERE!
  Status: 200
  Response: {"success":false,"msg":"update error"}

❌ API trả về: {"success":false,"msg":"update error"}

[Take screenshot of both expanders + error message]
[Paste to chat]
```

---

## 📸 Screenshot Example

**What to capture:**

```
┌─────────────────────────────────────┐
│ 🔍 Debug - Gia hạn         [Expand]│ ← Click to open
│   Old expiry: 1732867200000         │
│   New expiry: 1735459200000         │
│   Diff days: 30.0                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🔍 Debug Response          [Expand]│ ← Click to open
│   Status: 200                       │
│   Response: {"success":false,...}   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ❌ API trả về: {"success":false...}│ ← Error message
└─────────────────────────────────────┘
```

**Capture ALL 3 sections in 1 screenshot!**

---

## ⚡ Super Quick (1 minute)

**Fastest test possible:**

```bash
1. Run: streamlit run vpn_admin_pro_multiserver.py
2. Select server
3. Click 👥 Quản Lý User
4. Click any 🔄 button
5. Open debug expanders
6. Screenshot if fail
7. Done!
```

**Total time: < 1 minute**

---

## 🎯 Summary

**Debug mode gives you:**

✅ Exact request details  
✅ Exact response details  
✅ Exact error message  
✅ Full traceback  

**No more guessing!**

**Just:**

1. Test operation (30s)
2. Open debug expanders (10s)
3. Screenshot if fail (10s)
4. Report exact error (10s)

**Total: 1 minute to diagnose!**

---

🔍 **TRY IT NOW - SEE EXACT ERROR!** 🔍

**Version:** v2.3.3  
**Type:** Quick Test Guide  
**Time:** 3 minutes
