# ⚡ MULTI-SERVER QUICK START

## 🚀 Chạy trong 3 phút

### 1️⃣ Chạy app
```bash
bash run_multiserver.sh
```

Truy cập: `http://YOUR_IP:8501`

---

### 2️⃣ Thêm Server đầu tiên

1. Vào menu **🖥️ Quản lý Server**
2. Tab **➕ Thêm Server Mới**
3. Điền form:

```
Tên Server:    VPS Singapore 01
HOST:          http://123.45.67.89:8001
Username:      admin
Password:      your_password
Ghi chú:       Server cho khách VIP
```

4. Click **✅ Thêm Server**
5. Đợi test connection → ✅ OK!

---

### 3️⃣ Thêm Server thứ 2, 3...

Lặp lại bước 2 cho mỗi VPS:

```
Server 1: VPS Singapore
Server 2: VPS Japan  
Server 3: VPS USA
...
```

---

### 4️⃣ Xem tổng quan

1. Vào menu **🌍 Tổng Quan Toàn Hệ Thống**
2. Xem metrics:
   - 🖥️ Tổng Server: 3
   - 🟢 Server Online: 3
   - 👥 Tổng User: 150
   - 📊 Tổng Traffic: 450 GB

3. Xem bảng chi tiết từng server
4. Xem biểu đồ User/Traffic

---

### 5️⃣ Làm việc với 1 server

1. **Chọn Server** từ dropdown sidebar:
   ```
   📡 Chọn Server: [VPS Singapore 01]
   ```

2. Vào các menu:
   - **📊 Dashboard Server** - Xem chi tiết
   - **➕ Tạo User** - Tạo user mới
   - **👥 Quản Lý User** - Quản lý user

3. Switch server khác: Chọn lại dropdown

---

## 🎯 5 TÍNH NĂNG CHÍNH

### 1. 🌍 Tổng Quan Toàn Hệ Thống

**Xem gì:**
- Tổng server, Online/Offline
- Tổng user toàn bộ
- Tổng traffic
- Bảng so sánh server
- Biểu đồ phân bổ

**Khi nào dùng:**
- Mỗi sáng check hệ thống
- Báo cáo cho sếp
- Phát hiện server offline

---

### 2. 📊 Dashboard Server

**Xem gì:**
- Chi tiết 1 server cụ thể
- Metrics: Users, Traffic, CPU, RAM
- Top users
- Protocol stats

**Khi nào dùng:**
- Check chi tiết 1 server
- Giám sát performance

---

### 3. ➕ Tạo User

**Làm gì:**
- Tạo user mới trên server đang chọn
- Giống Single-Server

**Lưu ý:**
- User thuộc server hiện tại
- IP trong link là IP server đó

---

### 4. 👥 Quản Lý User

**Làm gì:**
- Reset traffic
- Gia hạn
- Bật/Tắt
- Xóa user

**Lưu ý:**
- Chỉ user trên server hiện tại

---

### 5. 🖥️ Quản Lý Server (⭐ Đặc biệt)

**Làm gì:**
- Thêm server mới
- Xóa server cũ
- Test connection
- Xem danh sách

**Khi nào dùng:**
- Setup lần đầu
- Mua VPS mới
- Retire VPS cũ

---

## 📁 FILE QUAN TRỌNG

### `servers_config.json`

**Chứa gì:**
- Danh sách tất cả server
- HOST, Username, Password
- Ghi chú

**Ở đâu:**
- Cùng folder với app

**Backup:**
```bash
cp servers_config.json servers_config.backup.json
```

**Restore:**
```bash
cp servers_config.backup.json servers_config.json
```

---

## 🎯 WORKFLOW HÀNG NGÀY

### Buổi sáng
```
1. Vào "Tổng Quan"
2. Check: Có server offline không?
3. Check: Tổng user/traffic
4. Note: Server nào cần quan tâm
```

### Có khách mới
```
1. Chọn server ít user nhất (load balancing)
2. Tạo user
3. Gửi link cho khách
```

### Khách báo lỗi
```
1. Hỏi IP khách đang dùng
2. Chọn server tương ứng
3. Tìm user → Xử lý
```

---

## 💡 TIPS

### Đặt tên Server

✅ **Tốt:**
```
VPS Singapore - Premium
VPS Japan - Backup
VPS USA West - Gaming
```

❌ **Không tốt:**
```
Server 1
Server 2
VPS
```

---

### Load Balancing

**Chiến lược đơn giản:**
```
1. Vào "Tổng Quan"
2. Xem server nào ít user nhất
3. Tạo user mới trên server đó
```

---

### Backup thường xuyên

```bash
# Backup danh sách server
cp servers_config.json ~/backup/

# Backup data từng server
# Vào Menu Hệ Thống → Backup (mỗi server)
```

---

## 🆘 TROUBLESHOOTING

### "Chưa có server nào"
→ Thêm server: Menu "Quản lý Server"

### "Không kết nối được server X"
→ Click "Test" bên cạnh server đó
→ Check HOST/Username/Password

### File `servers_config.json` mất
→ Restore từ backup
→ Hoặc thêm lại thủ công

---

## 📊 SO SÁNH vs SINGLE-SERVER

| Feature | Single | Multi |
|---------|--------|-------|
| Số server | 1 | Nhiều |
| Switch server | Không | ✅ |
| Tổng quan | Không | ✅ |
| Phù hợp | 1 VPS | 2+ VPS |

---

## ✅ CHECKLIST

### Lần đầu
- [ ] Chạy app
- [ ] Thêm Server 1
- [ ] Test → OK
- [ ] Thêm Server 2, 3...
- [ ] Vào "Tổng Quan"
- [ ] Tạo 1 user test
- [ ] Backup `servers_config.json`

### Hàng ngày
- [ ] Check "Tổng Quan"
- [ ] Xử lý requests
- [ ] Note server cần quan tâm

---

## 🎉 DONE!

Giờ bạn có thể:

✅ Quản lý **nhiều server** trong 1 giao diện  
✅ Switch server **1 click**  
✅ Xem **tổng quan** toàn hệ thống  
✅ **Load balance** giữa các server

**Chi tiết đầy đủ:** Đọc `MULTISERVER_GUIDE.md`

---

*Multi-Server Quick Start*  
*28/11/2024*
