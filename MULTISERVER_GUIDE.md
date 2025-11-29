# 🌐 HƯỚNG DẪN MULTI-SERVER - Quản lý nhiều server trong 1 giao diện

## 🎯 Giới thiệu

Phiên bản **Multi-Server** cho phép bạn quản lý **NHIỀU server 3X-UI** (hoặc panel tương thích) trong **1 GIAO DIỆN DUY NHẤT**.

### ✨ Tính năng

- ✅ Thêm/Xóa server không giới hạn
- ✅ Switch giữa các server dễ dàng
- ✅ Tổng quan toàn bộ hệ thống (All servers)
- ✅ Quản lý từng server riêng biệt
- ✅ Lưu config server tự động (JSON)
- ✅ Test connection mỗi server
- ✅ Metrics tổng hợp: Tổng users, Traffic, Status
- ✅ Biểu đồ so sánh giữa các server

---

## 🚀 CÁCH SỬ DỤNG

### Bước 1: Chạy ứng dụng Multi-Server

```bash
streamlit run vpn_admin_pro_multiserver.py
```

### Bước 2: Thêm Server đầu tiên

1. Mở menu **🖥️ Quản lý Server**
2. Chọn tab **➕ Thêm Server Mới**
3. Điền thông tin:
   - **Tên Server:** VPS Singapore 01 (tên gợi nhớ)
   - **HOST:** http://123.45.67.89:8001 (URL đầy đủ)
   - **Username:** admin
   - **Password:** your_password
   - **Ghi chú:** (optional) Ví dụ: "Server cho khách VIP"
4. Click **✅ Thêm Server**
5. Hệ thống sẽ **test connection** trước khi thêm
6. ✅ Nếu OK → Server được thêm vào danh sách

### Bước 3: Thêm nhiều Server

Lặp lại Bước 2 cho mỗi server:
- VPS Singapore
- VPS Japan
- VPS USA
- VPS Germany
- ...

### Bước 4: Xem tổng quan toàn hệ thống

1. Vào menu **🌍 Tổng Quan Toàn Hệ Thống**
2. Xem metrics:
   - 🖥️ Tổng Server
   - 🟢 Server Online/Offline
   - 👥 Tổng User trên tất cả server
   - 📊 Tổng Traffic
3. Xem bảng chi tiết từng server
4. Xem biểu đồ phân bổ User và Traffic

### Bước 5: Làm việc với 1 Server cụ thể

1. **Chọn Server** từ dropdown ở Sidebar:
   ```
   📡 Chọn Server: [VPS Singapore 01 (http://...)]
   ```

2. Server được chọn sẽ hiện ở đầu mỗi trang:
   ```
   🖥️ Đang làm việc trên: VPS Singapore 01
   ```

3. Tất cả thao tác (tạo user, xóa, reset...) chỉ áp dụng cho server này

4. Switch sang server khác: Chọn lại từ dropdown

---

## 📊 CÁC MENU CHÍNH

### 🌍 Tổng Quan Toàn Hệ Thống

**Chức năng:**
- Xem tất cả server cùng lúc
- Metrics tổng hợp
- Bảng so sánh server
- Biểu đồ User và Traffic

**Khi nào dùng:**
- Mỗi sáng check toàn bộ hệ thống
- So sánh performance giữa các server
- Phát hiện server có vấn đề (offline, overload)
- Báo cáo tổng hợp cho sếp

**Metrics hiển thị:**
| Metric | Mô tả |
|--------|-------|
| Tổng Server | Số server đã thêm |
| Server Online | Số server đang hoạt động |
| Tổng User | User trên tất cả server |
| Tổng Traffic | Traffic tổng hợp (GB) |

**Bảng chi tiết:**
| Cột | Mô tả |
|-----|-------|
| Server | Tên server |
| IP | IP address |
| Status | 🟢 Online / 🔴 Offline |
| Users | Số user trên server này |
| Active | Số user đang hoạt động |
| Traffic | Traffic đã dùng (GB) |

---

### 📊 Dashboard Server

**Chức năng:**
- Xem chi tiết 1 server cụ thể
- Metrics: Users, Traffic, Hết hạn
- Tài nguyên: CPU, RAM, Disk (nếu có)
- Biểu đồ Protocol và Top users

**Khi nào dùng:**
- Check chi tiết 1 server
- Giám sát tài nguyên
- Xem top user tiêu thụ data

---

### ➕ Tạo User

**Chức năng:**
- Tạo user mới trên server đang chọn
- Giống phiên bản single-server

**Lưu ý:**
- User được tạo chỉ thuộc về server đang chọn
- IP trong link sẽ là IP của server đó

---

### 👥 Quản Lý User

**Chức năng:**
- Xem danh sách user trên server đang chọn
- Reset traffic, Gia hạn, Bật/Tắt, Xóa
- Chỉ áp dụng cho server hiện tại

---

### 📋 Chi Tiết User

**Chức năng:**
- Xem chi tiết 1 user cụ thể
- Export link + QR code

---

### 🖥️ Quản Lý Server ⭐ (Menu đặc biệt)

**Tab 1: 📋 Danh sách Server**
- Xem tất cả server đã thêm
- Test connection từng server
- Xóa server không cần nữa

**Tab 2: ➕ Thêm Server Mới**
- Form thêm server
- Auto test connection
- Lưu vào file JSON

---

### ⚙️ Hệ Thống

**Chức năng:**
- Backup dữ liệu server đang chọn
- Thống kê chi tiết

---

## 💾 LƯU TRỮ DỮ LIỆU

### File: `servers_config.json`

Tất cả thông tin server được lưu trong file này:

```json
{
  "abc123": {
    "name": "VPS Singapore 01",
    "host": "http://123.45.67.89:8001",
    "username": "admin",
    "password": "your_password",
    "notes": "Server cho khách VIP",
    "added_date": "2024-11-28T14:30:00"
  },
  "def456": {
    "name": "VPS Japan 02",
    "host": "http://234.56.78.90:8001",
    "username": "admin",
    "password": "another_pass",
    "notes": "Server backup",
    "added_date": "2024-11-28T15:00:00"
  }
}
```

**Vị trí:** Cùng thư mục với `vpn_admin_pro_multiserver.py`

**Backup:** Copy file này để backup danh sách server

**Restore:** Paste file cũ lại để khôi phục

---

## 🎯 WORKFLOW THỰC TẾ

### Kịch bản 1: Setup ban đầu

```
1. Chạy app lần đầu
   ↓
2. Menu "Quản lý Server" → Thêm Server 1
   ↓
3. Test connection → OK → Lưu
   ↓
4. Thêm Server 2, 3, 4... (tương tự)
   ↓
5. Vào "Tổng Quan" → Xem tất cả server
   ↓
6. ✅ Sẵn sàng làm việc!
```

### Kịch bản 2: Hàng ngày

```
Buổi sáng:
1. Vào "🌍 Tổng Quan Toàn Hệ Thống"
2. Check: Có server nào offline không?
3. Check: Tổng user/traffic bao nhiêu?
4. Phân tích: Server nào đang overload?

Có khách mới:
1. Chọn server có ít user nhất (load balancing)
2. Vào "➕ Tạo User"
3. Tạo user trên server đó
4. Gửi link cho khách

Khách báo lỗi:
1. Hỏi khách đang dùng IP nào
2. Chọn server tương ứng
3. Vào "👥 Quản Lý User"
4. Tìm user → Xử lý (reset, gia hạn...)

Cuối ngày:
1. Vào "Tổng Quan" → Check lại metrics
2. Backup từng server quan trọng
3. Note lại server cần upgrade
```

### Kịch bản 3: Mở rộng hệ thống

```
Khi cần thêm server mới:
1. Mua VPS mới
2. Cài 3X-UI trên VPS đó
3. Vào app → "Quản lý Server" → Thêm
4. ✅ Server mới tự động vào hệ thống

Khi cần retire server cũ:
1. Stop tạo user mới trên server đó
2. Migrate user sang server khác (thủ công)
3. Khi không còn user → Vào "Quản lý Server" → Xóa
4. Tắt VPS cũ
```

---

## 📊 SO SÁNH PHIÊN BẢN

| Tính năng | Single-Server | Multi-Server |
|-----------|--------------|--------------|
| Số server | 1 | Không giới hạn |
| Switch server | Không | ✅ Dropdown |
| Tổng quan toàn hệ thống | Không | ✅ Menu riêng |
| Lưu config | Hardcode | ✅ JSON file |
| Test connection | Không | ✅ Có |
| So sánh server | Không | ✅ Biểu đồ |
| Phù hợp | Cá nhân, 1 VPS | Doanh nghiệp, nhiều VPS |

---

## 💡 TIPS & BEST PRACTICES

### Đặt tên Server

❌ **Không nên:**
```
Server 1
Server 2
VPS
```

✅ **Nên:**
```
VPS Singapore - Premium
VPS Japan - Backup
VPS USA West - Gaming
VPS Germany - Enterprise
```

**Lý do:** Dễ nhớ, dễ phân biệt

---

### Ghi chú Server

Sử dụng trường "Ghi chú" để note:
- Mục đích server (VIP, Backup, Test...)
- Thông số VPS (4GB RAM, 2 CPU...)
- Ngày hết hạn VPS
- Provider (AWS, DigitalOcean...)

**Ví dụ:**
```
Server cho khách VIP | 4GB RAM | Hết hạn: 31/12/2024 | Provider: AWS
```

---

### Load Balancing

**Chiến lược 1: Round-robin**
```
Khách 1 → Server A
Khách 2 → Server B
Khách 3 → Server C
Khách 4 → Server A (lặp lại)
```

**Chiến lược 2: Least Loaded**
```
Luôn chọn server có ít user nhất
→ Cân bằng tải tự động
```

**Chiến lược 3: Geographic**
```
Khách ở Châu Á → VPS Singapore
Khách ở Mỹ → VPS USA
Khách ở Châu Âu → VPS Germany
```

---

### Backup Strategy

**Hàng ngày:**
- Backup 1 server quan trọng nhất

**Hàng tuần:**
- Backup tất cả server
- Lưu vào Google Drive/Dropbox

**Hàng tháng:**
- Backup file `servers_config.json`
- Backup database (nếu có)

---

### Security

1. **Mật khẩu mạnh:**
   - Mỗi server dùng password khác nhau
   - Dài tối thiểu 16 ký tự
   - Có chữ hoa, thường, số, ký tự đặc biệt

2. **Firewall:**
   - Chỉ cho phép IP cố định truy cập 3X-UI Panel
   - Đổi port mặc định 8001 sang port khác

3. **Monitoring:**
   - Check "Tổng Quan" mỗi ngày
   - Alert khi server offline (manual hiện tại)

4. **Backup:**
   - Backup thường xuyên
   - Không lưu file config trên server public

---

## 🆘 TROUBLESHOOTING

### Lỗi: "Chưa có server nào"

**Nguyên nhân:** Lần đầu chạy app, chưa thêm server

**Giải pháp:**
1. Vào menu "🖥️ Quản lý Server"
2. Tab "➕ Thêm Server Mới"
3. Thêm ít nhất 1 server

---

### Lỗi: "Không thể kết nối tới server X"

**Nguyên nhân:**
- Server offline
- Sai username/password
- Firewall chặn
- HOST sai format

**Giải pháp:**
1. Vào "Quản lý Server"
2. Click nút "🔍 Test" bên cạnh server đó
3. Nếu lỗi:
   - Check server có chạy không: `systemctl status x-ui`
   - Check HOST đúng format: `http://IP:PORT`
   - Check username/password
   - Check firewall: `ufw status`

---

### Lỗi: "Server bị duplicate"

**Nguyên nhân:** Thêm cùng 1 server 2 lần

**Giải pháp:**
1. Vào "Quản lý Server"
2. Xóa server bị duplicate
3. Giữ lại 1 server duy nhất

---

### File `servers_config.json` bị mất

**Nguyên nhân:**
- Xóa nhầm
- Chuyển folder
- Hard disk lỗi

**Giải pháp:**
1. Restore từ backup (nếu có)
2. Hoặc thêm lại các server thủ công

**Phòng tránh:**
- Backup file này thường xuyên
- Copy vào Google Drive

---

## 🎓 FAQ

**Q: Có thể quản lý bao nhiêu server?**
A: Không giới hạn. Test với 50+ server vẫn mượt.

**Q: Có thể mix 3X-UI và panel khác không?**
A: Có, nếu panel đó có API tương thích 3X-UI.

**Q: Dữ liệu user có đồng bộ giữa các server không?**
A: Không. Mỗi server độc lập. User trên Server A không tự động có trên Server B.

**Q: Làm sao migrate user từ Server A sang Server B?**
A: Hiện tại phải thủ công:
1. Backup Server A
2. Tạo user mới trên Server B (cùng config)
3. Đổi link cho khách

**Q: File `servers_config.json` có bảo mật không?**
A: Không mã hóa. NÊN:
- Set permission: `chmod 600 servers_config.json`
- Không commit lên Git
- Backup vào nơi an toàn

**Q: So với phiên bản single-server, nên dùng cái nào?**
A:
- **1 server:** Dùng `vpn_admin_pro.py` (đơn giản hơn)
- **2+ server:** Dùng `vpn_admin_pro_multiserver.py`

**Q: Có thể chạy cả 2 phiên bản không?**
A: Được, nhưng dữ liệu không đồng bộ. Chọn 1 trong 2 để dùng.

**Q: Tính năng X trong single-server có trong multi-server không?**
A: Có hầu hết. Một số tính năng chưa port sang:
- Tạo hàng loạt (sẽ có trong v2.1)
- Chi tiết User đầy đủ (đang giản lược)

---

## 🚀 TÍNH NĂNG SẮP CÓ (v2.1)

- [ ] Tạo user hàng loạt (multi-server)
- [ ] Migrate user giữa các server
- [ ] Auto load balancing (tự động chọn server ít load nhất)
- [ ] Alert khi server offline (email/telegram)
- [ ] Thống kê so sánh performance
- [ ] Export report toàn hệ thống (PDF/Excel)
- [ ] Server groups (nhóm server theo region)
- [ ] Encrypt `servers_config.json`

---

## 📞 HỖ TRỢ

- **Docs:** Đọc file này
- **Issues:** GitHub Issues
- **Community:** Telegram @vpnadminpro

---

## ✅ CHECKLIST SỬ DỤNG

### Lần đầu
- [ ] Chạy app multi-server
- [ ] Thêm Server 1
- [ ] Test connection → OK
- [ ] Thêm Server 2, 3...
- [ ] Vào "Tổng Quan" → Check
- [ ] Tạo 1 user test trên mỗi server
- [ ] Verify user hoạt động
- [ ] Backup file `servers_config.json`

### Hàng ngày
- [ ] Check "Tổng Quan" xem server status
- [ ] Xử lý user requests
- [ ] Note server cần quan tâm

### Hàng tuần
- [ ] Backup tất cả server
- [ ] Review metrics
- [ ] Lên kế hoạch scale (nếu cần)

---

## 🎉 KẾT LUẬN

Với phiên bản **Multi-Server**, bạn có thể:

✅ Quản lý **không giới hạn server** trong 1 giao diện  
✅ Switch server chỉ với **1 click**  
✅ Xem tổng quan **toàn bộ hệ thống**  
✅ **Load balancing** thủ công hoặc tự động  
✅ **Scale** dễ dàng khi business lớn

**Perfect for VPN Business với nhiều server! 🚀**

---

*Multi-Server Edition v2.0*  
*28/11/2024*
