# 📝 HƯỚNG DẪN: Quản lý User Nâng cao

## 🆕 Tính năng mới v2.3

### ✅ Đã thêm:

1. **✏️ Sửa User** - Chỉnh sửa thông tin user đã tạo
2. **🗑️ Xóa hàng loạt** - Select và xóa nhiều user cùng lúc

---

## 1️⃣ SỬA USER (Edit User)

### 🎯 Tính năng

Chỉnh sửa thông tin user đã tạo:
- ✅ Đổi tên user
- ✅ Thay đổi thời hạn (expiry date)
- ✅ Thay đổi data limit

### 📋 Cách sử dụng

**Bước 1:** Vào menu **"👥 Quản Lý User"**

**Bước 2:** Tìm user cần sửa → Click nút **"✏️"**

**Bước 3:** Form edit hiện ra:

```
┌────────────────────────────────────────┐
│ ✏️ Sửa User                            │
│ 🆔 Đang sửa: user_01 (ID: 123)        │
├────────────────────────────────────────┤
│ Tên khách hàng:  [user_01     ]       │
│ Thời hạn (ngày): [30          ]       │
│ Data Limit (GB): [50          ]       │
│                                        │
│ [💾 Lưu thay đổi] [❌ Hủy]            │
└────────────────────────────────────────┘
```

**Bước 4:** Sửa các thông tin:

- **Tên khách hàng:** Đổi tên user
- **Thời hạn:** Số ngày còn lại (tính từ bây giờ)
- **Data Limit:** GB (0 = unlimited)

**Bước 5:** Click **"💾 Lưu thay đổi"**
- Hệ thống cập nhật ngay
- Success → Reload tự động

**Bước 6:** Xác nhận:
- ✅ Tên mới hiển thị trong list
- ✅ Thời hạn mới được tính
- ✅ Data limit mới áp dụng

### ✅ Use Cases

#### Case 1: Đổi tên user
```
Khách đổi tên: "user_01" → "khach_VIP_A"

1. Click ✏️
2. Đổi tên: khach_VIP_A
3. Lưu
4. ✅ Tên mới hiện trong list
```

#### Case 2: Gia hạn thêm thời gian
```
User sắp hết hạn (còn 2 ngày)
Cần gia hạn thêm 30 ngày

1. Click ✏️
2. Thời hạn: 30 (ngày mới, không cộng dồn)
3. Lưu
4. ✅ User còn 30 ngày từ bây giờ
```

#### Case 3: Tăng/Giảm data limit
```
User hiện tại: 50GB
Cần nâng lên: 100GB

1. Click ✏️
2. Data Limit: 100
3. Lưu
4. ✅ User có data limit mới 100GB
```

#### Case 4: Chuyển sang unlimited
```
User hiện tại: 50GB
Muốn unlimited

1. Click ✏️
2. Data Limit: 0
3. Lưu
4. ✅ User giờ unlimited data
```

---

## 2️⃣ XÓA HÀNG LOẠT (Bulk Delete)

### 🎯 Tính năng

Xóa nhiều user cùng lúc thay vì xóa từng cái:
- ✅ Checkbox cho từng user
- ✅ "Chọn tất cả" để select hết
- ✅ Hiển thị số user đã chọn
- ✅ Xóa hàng loạt với confirm

### 📋 Cách sử dụng

**Bước 1:** Vào menu **"👥 Quản Lý User"**

**Bước 2:** Select user cần xóa:

**Cách 1: Chọn từng user**
```
┌─────────────────────────────────────┐
│ [☑️] ✅ user_01 - Port: 10001      │
│ [☑️] ✅ user_02 - Port: 10002      │
│ [ ] ✅ user_03 - Port: 10003       │  ← Không chọn
│ [☑️] ✅ user_04 - Port: 10004      │
└─────────────────────────────────────┘
```

**Cách 2: Chọn tất cả**
```
[☑️ Chọn tất cả]  ← Click để chọn hết
```

**Bước 3:** Khi đã chọn, thông báo hiện:
```
📋 Đã chọn: 3 user

[🗑️ Xóa hàng loạt]  [❌ Bỏ chọn]
```

**Bước 4:** Click **"🗑️ Xóa hàng loạt"**

**Bước 5:** Confirm:
```
⚠️ Xác nhận xóa 3 user đã chọn?

[✅ Xác nhận xóa hàng loạt]  [❌ Hủy xóa hàng loạt]
```

**Bước 6:** Click **"✅ Xác nhận"**
- Spinner: "Đang xóa 3 user..."
- Success: "✅ Đã xóa: 3 user"
- Auto reload

### ✅ Use Cases

#### Case 1: Xóa user hết hạn
```
Có 10 user, 5 user đã hết hạn cần xóa

1. Vào "Quản Lý User"
2. Tìm 5 user hết hạn (xem cột "Hết hạn")
3. Tick checkbox của 5 user đó
4. Click "Xóa hàng loạt"
5. Confirm
6. ✅ 5 user đã bị xóa
```

#### Case 2: Dọn dẹp user test
```
Có 20 user test (tên: test_01, test_02...)
Cần xóa hết để bắt đầu production

1. Tìm kiếm: "test"
2. Kết quả: 20 user test
3. Click "☑️ Chọn tất cả"
4. Click "Xóa hàng loạt"
5. Confirm
6. ✅ 20 user test đã xóa sạch
```

#### Case 3: Xóa user không hoạt động
```
Có 50 user, 15 user bị disable (❌)
Muốn xóa 15 user đó

1. Vào list
2. Tìm user có ❌ (disabled)
3. Tick 15 checkbox
4. Xóa hàng loạt
5. ✅ Done
```

#### Case 4: Xóa user theo data usage
```
User nào dùng hết data → Xóa

1. Xem cột "Data"
2. Tìm user: "50.00/50 GB" (đã dùng hết)
3. Select các user đó
4. Xóa hàng loạt
5. ✅ Clean!
```

---

## 🎨 Giao diện mới

### Layout User Card:

```
┌─────────────────────────────────────────────────────────┐
│ [☑️] ✅ user_01 - Port: 10001 - VLESS                  │
│      📊 Data: 25.5/50 GB | 📅 Hết hạn: 15/12/2024     │
│                                                         │
│      [🔄] [⏱️] [⏸️] [✏️] [🗑️]                          │
│       ↑    ↑    ↑    ↑    ↑                            │
│    Reset Extend Toggle Edit Delete                     │
└─────────────────────────────────────────────────────────┘
```

### 5 Nút action:

1. **🔄** = Reset traffic
2. **⏱️** = Gia hạn +30 ngày (quick)
3. **⏸️/▶️** = Tắt/Bật user
4. **✏️** = Sửa user (NEW!)
5. **🗑️** = Xóa user

### Bulk Actions:

```
┌────────────────────────────────────────┐
│ [☑️ Chọn tất cả]                       │
│                                        │
│ 📋 Đã chọn: 5 user                    │
│                                        │
│ [🗑️ Xóa hàng loạt] [❌ Bỏ chọn]      │
└────────────────────────────────────────┘
```

---

## 📊 So sánh Trước vs Sau

| Tính năng | v2.2 | v2.3 (NEW) |
|-----------|------|------------|
| **Xem user** | ✅ | ✅ |
| **Reset traffic** | ✅ | ✅ |
| **Gia hạn +30d** | ✅ | ✅ |
| **Toggle on/off** | ✅ | ✅ |
| **Xóa user** | ✅ 1 user | ✅ 1 hoặc nhiều |
| **Sửa user** | ❌ | ✅ NEW! |
| **Xóa hàng loạt** | ❌ | ✅ NEW! |
| **Checkbox select** | ❌ | ✅ NEW! |

---

## 🔒 An toàn & Validation

### Khi sửa user:
- ✅ Validate tên không trống
- ✅ Validate ngày > 0
- ✅ Validate data limit >= 0
- ✅ Giữ nguyên traffic đã dùng (up/down)
- ✅ Giữ nguyên protocol, port, settings

### Khi xóa hàng loạt:
- ✅ Hiển thị số user sẽ xóa
- ✅ Confirm trước khi xóa
- ✅ Hiển thị progress
- ✅ Báo cáo thành công/thất bại

---

## 🧪 Test Guide

### Test 1: Edit User
```bash
streamlit run vpn_admin_pro_multiserver.py

# 1. Chọn server
# 2. Vào "👥 Quản Lý User"
# 3. Click ✏️ ở user bất kỳ
# 4. Sửa tên: "user_01" → "test_edit"
# 5. Sửa thời hạn: 60 ngày
# 6. Sửa data: 100GB
# 7. Click "💾 Lưu"
# 8. Verify: Tên mới, thời gian mới trong list
```

### Test 2: Bulk Delete
```bash
# 1. Vào "Quản Lý User"
# 2. Có ít nhất 5 user
# 3. Tick 3 checkbox
# 4. Thấy: "📋 Đã chọn: 3 user"
# 5. Click "🗑️ Xóa hàng loạt"
# 6. Thấy confirm: "Xác nhận xóa 3 user?"
# 7. Click "✅ Xác nhận"
# 8. Thấy: "✅ Đã xóa: 3 user"
# 9. Verify: 3 user mất khỏi list
```

### Test 3: Select All
```bash
# 1. Có 10 user
# 2. Click "☑️ Chọn tất cả"
# 3. Verify: Tất cả checkbox được tick
# 4. Thấy: "Đã chọn: 10 user"
# 5. Click "❌ Bỏ chọn"
# 6. Verify: Tất cả checkbox bỏ tick
```

---

## 💡 Tips & Best Practices

### Tip 1: Backup trước khi xóa hàng loạt
```
1. Vào "⚙️ Hệ Thống"
2. Click "💾 Download JSON"
3. Lưu backup
4. Mới thực hiện xóa hàng loạt
```

### Tip 2: Tìm kiếm trước khi xóa
```
Muốn xóa tất cả user test:
1. Tìm kiếm: "test"
2. Kết quả: Chỉ user test
3. Chọn tất cả
4. Xóa hàng loạt
→ Chỉ xóa user test, không động vào user khác
```

### Tip 3: Sửa user thay vì xóa-tạo lại
```
❌ Cách cũ (lâu):
1. Xóa user
2. Tạo user mới
3. Gửi link mới cho khách

✅ Cách mới (nhanh):
1. Click ✏️
2. Sửa thông tin
3. Lưu
→ User giữ nguyên link, chỉ thay đổi config
```

### Tip 4: Gia hạn hàng loạt
```
Nhiều user cần gia hạn:

Cách 1 (Quick - Chỉ +30d):
1. Click ⏱️ từng user

Cách 2 (Flexible - Tùy chỉnh số ngày):
1. Click ✏️
2. Đặt số ngày tùy ý
3. Lưu
```

---

## 🔧 Technical Details

### API Endpoints Used:

**Update User:**
```
POST {host}/xui/inbound/update/{id}
Data: {
  "remark": "new_name",
  "expiryTime": timestamp_ms,
  "total": bytes,
  "up": current_up,
  "down": current_down,
  "enable": true/false,
  ...
}
```

**Bulk Delete:**
```
Loop {
  POST {host}/xui/inbound/del/{id}
}
```

### Session State:

```python
st.session_state.selected_users = [id1, id2, ...]
st.session_state.edit_mode_{id} = True/False
st.session_state.confirm_bulk_delete = True/False
```

---

## 📞 Troubleshooting

### Vấn đề 1: Sửa user không lưu

**Nguyên nhân:** Connection timeout

**Fix:**
1. Test kết nối server (Click 🔍 ở "Quản Lý Server")
2. Kiểm tra network
3. Thử lại

### Vấn đề 2: Xóa hàng loạt chỉ xóa được 1 phần

**Nguyên nhân:** Một số user không tồn tại hoặc lỗi API

**Check:**
```
Thông báo: "✅ Đã xóa: 5 user"
           "❌ Lỗi: 2 user"

→ 5 user xóa OK, 2 user lỗi
```

**Fix:** Refresh page và xóa lại 2 user lỗi

### Vấn đề 3: Checkbox không tick được

**Nguyên nhân:** Browser cache

**Fix:**
1. Hard refresh: Ctrl+F5
2. Hoặc clear cache
3. Restart Streamlit

---

**Version:** v2.3 - Enhanced User Management  
**Date:** 29/11/2024  
**Status:** ✅ READY TO USE

🚀 **ENJOY ADVANCED USER MANAGEMENT!** 🚀
