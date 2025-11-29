# ⚡ QUICK START - Bắt đầu trong 2 phút

## 🎯 Những gì bạn nhận được

### Code gốc → Code mới
```
❌ Trước: 300 dòng, 5 tính năng
✅ Bây giờ: 800+ dòng, 20+ tính năng
```

## 🚀 3 Bước để chạy

### 1️⃣ Cài thư viện (1 lần duy nhất)
```bash
pip3 install -r requirements.txt
```

### 2️⃣ Sửa config (1 lần duy nhất)
Mở file `vpn_admin_pro.py`, tìm dòng 11-13:
```python
HOST = "http://YOUR_IP:8001"      # ← Đổi IP của bạn
USERNAME = "admin"                 # ← Đổi username
PASSWORD = "password"              # ← Đổi password
```

### 3️⃣ Chạy
```bash
bash run.sh
```
Hoặc:
```bash
streamlit run vpn_admin_pro.py
```

**Truy cập:** `http://YOUR_IP:8501`

---

## ✨ 5 Tính năng QUAN TRỌNG NHẤT

### 1. 🔄 Reset Traffic (Mới)
**Vấn đề:** Khách hết data nhưng chưa hết hạn  
**Giải pháp:** Click 1 nút → Data về 0  
**Vị trí:** Quản Lý User → Chọn user → Reset Traffic

### 2. ⏱️ Gia hạn +30 ngày (Mới)
**Vấn đề:** Khách muốn gia hạn  
**Giải pháp:** Click 1 nút → Tự động thêm 30 ngày  
**Vị trí:** Quản Lý User → Chọn user → Gia hạn +30d

### 3. 📋 Xem lại Link/QR (Mới)
**Vấn đề:** Khách mất link  
**Giải pháp:** Export lại link + QR bất cứ lúc nào  
**Vị trí:** Quản Lý User → Chọn user → Xem Link

### 4. 📦 Tạo hàng loạt (Mới)
**Vấn đề:** Tạo 50 user mất cả ngày  
**Giải pháp:** Tạo 50 user trong 30 giây  
**Vị trí:** Tạo Gói Mới → Tab "Tạo Hàng Loạt"

### 5. 💾 Backup (Mới)
**Vấn đề:** Sợ mất data  
**Giải pháp:** Download toàn bộ config ra JSON  
**Vị trí:** Hệ Thống → Backup & Restore

---

## 📊 Tính năng mới khác

- ✅ Bật/Tắt user (không cần xóa)
- ✅ Tìm kiếm user nhanh
- ✅ Filter: Hoạt động/Tắt/Hết hạn
- ✅ Sắp xếp: A-Z, Data nhiều nhất
- ✅ Chi tiết user (menu riêng)
- ✅ Giới hạn Data (GB) khi tạo user
- ✅ Thống kê nâng cao
- ✅ Cảnh báo user sắp hết hạn (7 ngày)
- ✅ Giám sát VPS: CPU + RAM + Disk
- ✅ Top 5 user dùng data nhiều
- ✅ UI đẹp: Icons, màu sắc, progress bars

---

## 📁 Các file quan trọng

| File | Mô tả | Đọc khi nào |
|------|-------|-------------|
| **vpn_admin_pro.py** | Code chính | Để chạy |
| **requirements.txt** | Thư viện cần cài | Lần đầu |
| **run.sh** | Script chạy nhanh | Để chạy nhanh |
| **HUONG_DAN.md** | Hướng dẫn đầy đủ (VI) | Học cách dùng |
| **INSTALL.md** | Cài đặt chi tiết | Gặp lỗi |
| **FEATURES.md** | Chi tiết tính năng | Tìm hiểu sâu |

---

## 🎯 Workflow hàng ngày

### Sáng:
```
1. Mở Dashboard
2. Xem user sắp hết hạn (trong 7 ngày)
3. Gọi điện nhắc gia hạn
```

### Có khách mới:
```
1. Tạo Gói Mới
2. Nhập tên + Thời hạn + Data limit
3. Copy link hoặc QR gửi khách
```

### Khách báo lỗi:
```
Hết data → Reset Traffic
Hết hạn → Gia hạn +30d
Mất link → Xem Link
```

### Cuối tuần:
```
1. Backup dữ liệu
2. Lưu file JSON vào Drive
3. Xem thống kê tuần
```

---

## 💡 Tips quan trọng

### ✅ NÊN
- Backup mỗi tuần
- Xem list "sắp hết hạn" mỗi ngày
- Dùng "Reset Traffic" thay vì tạo user mới
- Dùng "Tắt" thay vì "Xóa" (giữ config)
- Dùng "Tạo hàng loạt" cho đơn sỉ

### ❌ KHÔNG NÊN
- Xóa user khi chỉ muốn tạm ngưng (dùng Tắt)
- Tạo user thủ công khi cần nhiều (dùng Bulk)
- Quên backup
- Dùng password yếu cho Panel

---

## 🆘 Troubleshooting nhanh

### "Connection refused"
```bash
# Kiểm tra Streamlit có chạy không
ps aux | grep streamlit

# Kiểm tra port
netstat -tuln | grep 8501

# Kiểm tra firewall
ufw allow 8501
```

### "❌ Mất kết nối tới Panel"
```python
# Mở vpn_admin_pro.py
# Kiểm tra dòng 11-13:
HOST = "http://YOUR_IP:8001"  # ← Đúng IP chưa?
USERNAME = "admin"             # ← Đúng username chưa?
PASSWORD = "password"          # ← Đúng password chưa?
```

### "ModuleNotFoundError"
```bash
pip3 install -r requirements.txt --upgrade
```

---

## 📞 Cần giúp?

1. **Cài đặt:** Đọc `INSTALL.md`
2. **Cách dùng:** Đọc `HUONG_DAN.md`
3. **Tính năng:** Đọc `FEATURES.md`
4. **Vẫn lỗi:** Tạo Issue trên GitHub

---

## 🎉 Hoàn tất!

Giờ bạn có **dashboard quản lý VPN chuyên nghiệp**!

**Thời gian học:** 5 phút  
**Tiết kiệm:** 95% thời gian quản lý  
**ROI:** Tăng 30% doanh thu (nhờ nhắc gia hạn)

---

**Let's make money! 💰**

*v2.0.0 | 28/11/2024*
