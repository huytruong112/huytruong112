# 🧪 TEST THÊM SERVER - Hướng dẫn kiểm tra

## ✅ TEST CASE: Thêm nhiều server

### Bước 1: Chạy app
```bash
streamlit run vpn_admin_pro_multiserver.py
```

### Bước 2: Thêm Server đầu tiên

1. Menu "🖥️ Quản lý Server"
2. Tab "➕ Thêm Server Mới"
3. Điền:
   ```
   Tên:  Test Server 1
   HOST: http://74.81.55.39:8001
   User: admin
   Pass: password
   ```
4. Click "✅ Thêm Server"
5. Đợi 2 giây → App tự reload

**VERIFY:**
- ✅ Thấy "✅ Đã thêm server 'Test Server 1' thành công!"
- ✅ Sidebar hiện "✅ 1 server"
- ✅ Tab "Danh sách Server" hiện server vừa thêm
- ✅ Form đã reset (trống)

### Bước 3: Thêm Server thứ 2

1. Vẫn ở tab "➕ Thêm Server Mới"
2. Form đã trống (đã reset)
3. Điền:
   ```
   Tên:  Test Server 2
   HOST: http://45.119.84.238:8888/path
   User: admin
   Pass: password2
   ```
4. Click "✅ Thêm Server"
5. Đợi 2 giây → App tự reload

**VERIFY:**
- ✅ Thấy "✅ Đã thêm server 'Test Server 2' thành công!"
- ✅ Sidebar hiện "✅ 2 server"
- ✅ Tab "Danh sách Server" hiện 2 server
- ✅ Form đã reset lại

### Bước 4: Thêm Server thứ 3

Lặp lại Bước 3 với:
```
Tên:  Test Server 3
HOST: http://123.45.67.89:8001
```

**VERIFY:**
- ✅ Sidebar hiện "✅ 3 server"
- ✅ Tab "Danh sách Server" hiện 3 server

### Bước 5: Verify file config

```bash
cat servers_config.json
```

**Phải thấy:**
```json
{
  "abc123": {
    "name": "Test Server 1",
    ...
  },
  "def456": {
    "name": "Test Server 2",
    ...
  },
  "ghi789": {
    "name": "Test Server 3",
    ...
  }
}
```

✅ **PASS nếu thấy 3 server trong file!**

---

## 🔍 TROUBLESHOOTING

### Vấn đề: Sidebar vẫn hiện "0 server" sau khi thêm

**Fix:**
1. Click nút "🔄 Làm mới" ở sidebar
2. Hoặc F5 refresh page

### Vấn đề: Tab "Danh sách" không hiện server

**Fix:**
1. Click vào tab "Danh sách Server" lần nữa
2. Hoặc refresh page (F5)

### Vấn đề: Form không reset

**Nguyên nhân:** Browser cache

**Fix:**
1. Hard refresh: Ctrl + F5 (Windows) hoặc Cmd + Shift + R (Mac)
2. Clear browser cache

---

## ✅ CHECKLIST HOÀN CHỈNH

- [ ] Thêm Server 1 → Thành công
- [ ] Sidebar cập nhật → "✅ 1 server"
- [ ] Tab "Danh sách" hiện Server 1
- [ ] Form đã reset
- [ ] Thêm Server 2 → Thành công
- [ ] Sidebar cập nhật → "✅ 2 server"
- [ ] Tab "Danh sách" hiện Server 1 + 2
- [ ] Form đã reset lại
- [ ] Thêm Server 3 → Thành công
- [ ] Sidebar cập nhật → "✅ 3 server"
- [ ] Tab "Danh sách" hiện tất cả 3 server
- [ ] File config có 3 server

**TẤT CẢ PASS = ✅ HOẠT ĐỘNG HOÀN HẢO!**

---

*Test Guide - Updated: 28/11/2024*
