# 🛡️ VPN Admin Pro v2.0 - 3X-UI Management Dashboard

Giao diện quản lý VPN/Proxy hiện đại cho 3X-UI Panel với đầy đủ tính năng.

**🆕 v2.0:** Có 2 phiên bản - Single-Server (1 VPS) & Multi-Server (2+ VPS)

## 📦 2 Phiên bản

### 1️⃣ Single-Server Edition
**File:** `vpn_admin_pro.py`  
**Dùng cho:** 1 VPS duy nhất  
**Chạy:** `bash run.sh`

### 2️⃣ Multi-Server Edition 🆕
**File:** `vpn_admin_pro_multiserver.py`  
**Dùng cho:** 2+ VPS (không giới hạn)  
**Chạy:** `bash run_multiserver.sh`

**Chưa biết chọn cái nào?** → Đọc [WHICH_VERSION.md](WHICH_VERSION.md)

---

## ✨ Tính năng chính

### Single-Server: 20+ tính năng

### 📊 Dashboard
- Hiển thị tổng quan: Tổng user, user active, lưu lượng, hết hạn
- Giám sát tài nguyên server: CPU, RAM, Disk usage với progress bar
- Biểu đồ phân bổ giao thức (VLESS, VMess, ...)
- Top 5 user tiêu thụ data nhiều nhất

### ➕ Tạo User
**Tạo đơn:**
- Nhập tên khách hàng/email
- Chọn giao thức: VLESS hoặc VMess
- Thiết lập thời hạn (1-365 ngày)
- Giới hạn data (GB) hoặc unlimited
- Tự động tạo link kết nối + QR code

**Tạo hàng loạt:**
- Tạo nhiều user cùng lúc (tối đa 50)
- Tự động đặt tên theo prefix: user_001, user_002...
- Progress bar theo dõi tiến trình
- Xuất báo cáo kết quả

### 👥 Quản lý User
**Hiển thị danh sách:**
- Tìm kiếm theo tên/port
- Filter theo trạng thái: Tất cả/Hoạt động/Tắt/Hết hạn
- Sắp xếp: Mới nhất/Tên A-Z/Data nhiều nhất
- Hiển thị: Status, Port, Protocol, Data usage, Expiry date

**Hành động nhanh:**
- 🔄 **Reset Traffic**: Đặt lại lưu lượng về 0
- ⏱️ **Gia hạn +30 ngày**: Tự động gia hạn thêm 30 ngày
- ⏸️ **Bật/Tắt User**: Toggle trạng thái hoạt động
- 📋 **Xem Link**: Hiển thị link kết nối + QR code
- 🗑️ **Xóa User**: Xóa vĩnh viễn với xác nhận

### 📋 Chi tiết User
- Xem thông tin đầy đủ: Port, Protocol, Status, Expiry
- Chi tiết lưu lượng: Upload, Download, Total, Giới hạn
- Cấu hình kỹ thuật: UUID, Stream Settings, Full JSON config
- Export link và QR code

### ⚙️ Hệ thống
**Backup & Restore:**
- Tải xuống backup toàn bộ config dạng JSON
- Bao gồm: User info, Port, Protocol, Traffic, Expiry
- File đặt tên theo timestamp: vpn_backup_20241128_143052.json
- Upload để restore (đang phát triển)

**Thống kê:**
- Phân tích theo Protocol: Số user, Tổng traffic
- Thống kê trạng thái: Hoạt động/Tắt/Hết hạn
- Cảnh báo user sắp hết hạn (trong 7 ngày)

**Cấu hình:**
- Xem thông tin kết nối Panel
- Test connection
- Làm mới cache
- Thông tin phiên bản

## 🚀 Quick Start

### Single-Server (1 VPS)

```bash
# 1. Cài dependencies
pip3 install -r requirements.txt

# 2. Sửa config (dòng 11-13 trong vpn_admin_pro.py)
HOST = "http://YOUR_IP:8001"
USERNAME = "admin"
PASSWORD = "your_password"

# 3. Chạy
bash run.sh

# 4. Truy cập
http://YOUR_IP:8501
```

**Chi tiết:** [QUICK_START.md](QUICK_START.md)

---

### Multi-Server (2+ VPS) 🆕

```bash
# 1. Cài dependencies
pip3 install -r requirements.txt

# 2. Chạy
bash run_multiserver.sh

# 3. Thêm server qua UI
Menu "Quản lý Server" → Thêm Server

# 4. Sử dụng
Switch server từ dropdown → Quản lý như bình thường
```

**Chi tiết:** [MULTISERVER_QUICKSTART.md](MULTISERVER_QUICKSTART.md)

## 📖 Hướng dẫn sử dụng

### Tạo user mới
1. Vào menu **➕ Tạo Gói Mới**
2. Nhập tên khách hàng (ví dụ: `khach_vip_01`)
3. Chọn giao thức (VLESS hoặc VMess)
4. Thiết lập thời hạn (ngày)
5. Nhập giới hạn data (0 = unlimited)
6. Click **✨ Kích Hoạt Ngay**
7. Sao chép link hoặc quét QR code để cung cấp cho khách

### Quản lý user hiện có
1. Vào menu **👥 Quản Lý User**
2. Tìm user cần thao tác
3. Chọn user từ dropdown
4. Sử dụng các nút hành động:
   - Reset traffic: Khi user hết data nhưng chưa hết hạn
   - Gia hạn: Thêm 30 ngày từ thời hạn hiện tại
   - Bật/Tắt: Tạm ngưng/Kích hoạt lại
   - Xem Link: Lấy lại link kết nối
   - Xóa: Gỡ bỏ user khỏi hệ thống

### Backup dữ liệu
1. Vào menu **⚙️ Hệ Thống**
2. Tab **💾 Backup & Restore**
3. Click **📥 Tải xuống Backup**
4. Click **💾 Download JSON File**
5. Lưu file JSON vào máy tính

## 🌐 Multi-Server Features (Bonus!)

Phiên bản Multi-Server cho phép:

- ✅ **Quản lý không giới hạn server** trong 1 giao diện
- ✅ **Switch server** chỉ với 1 click
- ✅ **Tổng quan toàn hệ thống** - Xem tất cả server cùng lúc
- ✅ **So sánh server** - Biểu đồ, Metrics
- ✅ **Thêm/Xóa server** qua UI (không edit code)
- ✅ **Test connection** từng server
- ✅ **Load balancing** - Chọn server ít user nhất

**Yêu cầu:**
> "khi có nhiều cấu hình khác nhau, nhiều server 3x-ui hoặc các panel khác thì làm thế nào để quản lý chung 1 trang quản trị"

✅ **Đã giải quyết hoàn toàn!**

Đọc chi tiết: [MULTISERVER_GUIDE.md](MULTISERVER_GUIDE.md)

---

## 🔧 Troubleshooting

### Lỗi kết nối Panel
- Kiểm tra HOST, USERNAME, PASSWORD trong code
- Đảm bảo 3X-UI Panel đang chạy
- Kiểm tra firewall/port

### User không thể kết nối
- Kiểm tra VPS_IP có đúng IP public không
- Đảm bảo port đã mở trên firewall
- Kiểm tra user chưa hết hạn/hết data

### Lỗi import module
```bash
pip install -r requirements.txt --upgrade
```

## 📚 Documentation

### 🔴 Quick Start (5 phút)
- [00_START_HERE.md](00_START_HERE.md) - Điểm vào
- [QUICK_START.md](QUICK_START.md) - Single-Server 2 phút
- [MULTISERVER_QUICKSTART.md](MULTISERVER_QUICKSTART.md) - Multi-Server 3 phút
- [WHICH_VERSION.md](WHICH_VERSION.md) - Chọn phiên bản

### 🟡 Complete Guides
- [HUONG_DAN.md](HUONG_DAN.md) - Single-Server chi tiết (VI)
- [MULTISERVER_GUIDE.md](MULTISERVER_GUIDE.md) - Multi-Server chi tiết (VI)
- [INSTALL.md](INSTALL.md) - Installation & Troubleshooting (EN)
- [FEATURES.md](FEATURES.md) - Technical features (EN)

### 🟢 References
- [INDEX.md](INDEX.md) - Navigation
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [SUMMARY.md](SUMMARY.md) - Project overview

**Tổng:** 20+ documentation files

---

## 📝 Changelog

### Version 2.0 (Current)
- ✅ Dashboard với real-time monitoring
- ✅ Tạo user hàng loạt
- ✅ Quản lý user đầy đủ (Reset, Gia hạn, Toggle)
- ✅ Chi tiết user với full config
- ✅ Backup/Restore
- ✅ Thống kê nâng cao
- ✅ Export link + QR code
- ✅ Tìm kiếm, filter, sort

### Version 1.0 (Ban đầu)
- Dashboard cơ bản
- Tạo user đơn
- Xem danh sách và xóa user

## 🛠️ Tính năng sắp có

- [ ] Restore từ backup file
- [ ] Chỉnh sửa user (đổi port, đổi tên)
- [ ] Thông báo/Alert khi user sắp hết hạn
- [ ] Export Excel/CSV
- [ ] Multi-language support
- [ ] API endpoint cho tích hợp
- [ ] Logs và audit trail
- [ ] Hỗ trợ Trojan protocol

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Tạo Pull Request hoặc Issue để báo lỗi/đề xuất tính năng.

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

## 💬 Liên hệ & Hỗ trợ

- Issues: Tạo issue trên GitHub
- Email: admin@example.com
- Telegram: @vpnadminpro

---

**Lưu ý:** Ứng dụng này được thiết kế để quản lý 3X-UI Panel. Đảm bảo bạn có quyền truy cập và hiểu rõ về cấu hình VPN/Proxy trước khi sử dụng.
