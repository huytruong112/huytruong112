# 📋 Changelog

Tất cả các thay đổi quan trọng của dự án sẽ được ghi lại ở đây.

## [2.0.0] - 2024-11-28

### ✨ Tính năng mới

#### Dashboard
- ✅ Thêm metric "User đã hết hạn"
- ✅ Giám sát CPU, RAM, Disk với progress bar
- ✅ Top 5 user tiêu thụ data nhiều nhất
- ✅ Biểu đồ phân bổ protocol
- ✅ Hiển thị thời gian real-time

#### Quản lý User
- ✅ **Reset Traffic**: Đặt lại upload/download về 0
- ✅ **Gia hạn tự động**: Thêm 30 ngày với 1 click
- ✅ **Toggle Enable/Disable**: Tạm ngưng user không xóa
- ✅ **Xem Link**: Export lại link + QR cho user cũ
- ✅ **Tìm kiếm**: Theo tên hoặc port
- ✅ **Filter**: Tất cả/Hoạt động/Tắt/Hết hạn
- ✅ **Sắp xếp**: Mới nhất/A-Z/Data nhiều nhất
- ✅ **Xác nhận xóa**: Popup confirmation trước khi xóa

#### Tạo User
- ✅ **Giới hạn Data**: Thiết lập GB limit cho mỗi user
- ✅ **Tạo hàng loạt**: Bulk create 1-50 user cùng lúc
- ✅ **Progress tracking**: Thanh tiến trình khi tạo nhiều user
- ✅ **Báo cáo kết quả**: Bảng tóm tắt thành công/thất bại
- ✅ **Preview expiry**: Hiển thị ngày hết hạn trước khi tạo

#### Chi tiết User (Menu mới)
- ✅ Xem thông tin đầy đủ: Port, Protocol, Status, Expiry
- ✅ Chi tiết lưu lượng: Upload, Download, Total, Limit
- ✅ Cấu hình kỹ thuật: UUID, Stream Settings, Full JSON
- ✅ Export link và QR code full size

#### Hệ thống
- ✅ **Backup**: Download toàn bộ config ra JSON
- ✅ **Thống kê theo Protocol**: User count + Traffic
- ✅ **Thống kê trạng thái**: Active/Disabled/Expired
- ✅ **Cảnh báo hết hạn**: List user sắp hết hạn trong 7 ngày
- ✅ **Test Connection**: Kiểm tra kết nối Panel
- ✅ **Clear Cache**: Làm mới dữ liệu

### 🎨 Cải thiện UI/UX

- ✅ Emoji icons cho mọi menu và action
- ✅ Color-coded status indicators
- ✅ Progress bars cho metrics
- ✅ Interactive dataframes với column config
- ✅ Tabs để phân nhóm tính năng
- ✅ Containers với borders
- ✅ Success/Error messages với icons
- ✅ Loading spinners cho API calls
- ✅ Balloons animation khi tạo user thành công
- ✅ Modal popups cho actions

### 🔧 Technical

#### API Functions mới:
```python
def update_inbound()      # Cập nhật thông tin inbound
def toggle_inbound()      # Bật/tắt user
def reset_traffic()       # Reset lưu lượng
def extend_expiry()       # Gia hạn thời gian
def generate_link()       # Tạo link từ config
def backup_config()       # Export JSON backup
```

#### Helper Functions:
```python
def get_system_stats()    # Đầy đủ: CPU, RAM, Disk
def generate_qr()         # Tạo QR code
def get_public_ip()       # Parse IP từ HOST
```

### 📚 Documentation

- ✅ README.md: Hướng dẫn tổng quan
- ✅ FEATURES.md: Chi tiết tính năng
- ✅ INSTALL.md: Hướng dẫn cài đặt chi tiết
- ✅ CHANGELOG.md: Lịch sử thay đổi
- ✅ config.example.py: Template cấu hình
- ✅ run.sh: Script khởi chạy nhanh

### 🐛 Bug Fixes

- ✅ Fix parse settings JSON error
- ✅ Handle expired time = 0 (unlimited)
- ✅ Proper error handling cho tất cả API calls
- ✅ Fix RAM calculation (bytes to GB)
- ✅ Handle empty inbound list
- ✅ Proper date formatting

### 🔒 Security

- ✅ Session management
- ✅ API timeout controls
- ✅ Input validation
- ✅ Confirmation cho hành động nguy hiểm

---

## [1.0.0] - 2024-11-27 (Code gốc)

### ✅ Có sẵn

- Dashboard cơ bản
- Hiển thị user count, traffic
- RAM monitoring
- Tạo user đơn (VLESS/VMess)
- Generate link + QR khi tạo mới
- Xem danh sách user
- Xóa user
- Protocol chart

### ❌ Chưa có

- Reset traffic
- Gia hạn user
- Toggle enable/disable
- Xem link cho user cũ
- Tìm kiếm, filter, sort
- Chi tiết user
- Tạo hàng loạt
- Data limit
- Backup/Restore
- Thống kê chi tiết
- CPU, Disk monitoring
- Xác nhận xóa
- Nhiều tính năng UX

---

## 🚀 Upcoming (Roadmap)

### [2.1.0] - Planning
- [ ] Restore from backup JSON
- [ ] Edit user (port, UUID, protocol)
- [ ] Custom extend days (không chỉ +30)
- [ ] Export Excel/CSV
- [ ] Bulk delete
- [ ] Bulk operations (reset traffic, extend nhiều user)

### [2.2.0] - Planning
- [ ] Email notifications (user sắp hết hạn)
- [ ] Webhook support
- [ ] API endpoints cho tích hợp
- [ ] Logs và audit trail
- [ ] User activity tracking

### [3.0.0] - Long-term
- [ ] Multi-server management
- [ ] User portal (self-service)
- [ ] Payment integration
- [ ] Trojan protocol support
- [ ] Docker deployment
- [ ] Multi-language (EN, VI, ZH)

---

## 📝 Notes

### Breaking Changes
- Không có (backward compatible với v1.0)

### Dependencies Changes
```diff
streamlit>=1.28.0    (unchanged)
requests>=2.31.0     (unchanged)
pandas>=2.0.0        (unchanged)
qrcode>=7.4.2        (unchanged)
Pillow>=10.0.0       (unchanged)
psutil>=5.9.5        (unchanged)
```

### Migration Guide
Nếu đang dùng v1.0:
1. Backup file cũ: `cp vpn_admin_pro.py vpn_admin_pro.py.v1.bak`
2. Thay file mới
3. Kiểm tra HOST, USERNAME, PASSWORD vẫn đúng
4. Chạy lại: `streamlit run vpn_admin_pro.py`
5. Tất cả data user cũ vẫn giữ nguyên (lưu trên 3X-UI Panel)

---

**Tổng kết:**
- **Từ:** 1 file Python đơn giản (~300 dòng)
- **Đến:** Full-featured admin panel (~800+ dòng)
- **Tăng:** 15+ tính năng mới
- **Cải thiện:** UI/UX toàn diện
- **Thêm:** 5 file documentation

*Phát triển bởi: VPN Admin Pro Team*
