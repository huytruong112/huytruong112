# 📂 Cấu Trúc File Project

## 🗂️ Tổng Quan

```
webhook-payment-system/
├── 🔥 Core Files (API & Logic)
│   ├── api_payment_webhook.php           # API webhook chính (production)
│   ├── api_payment_webhook_v2.php        # Version có DB logging
│   ├── check_transaction_status.php      # API kiểm tra trạng thái GD
│   ├── check_balance.php                 # API kiểm tra số dư
│   ├── payment.php                       # Logic mua gói dịch vụ
│   └── deposit.php                       # Trang nạp tiền (frontend)
│
├── ⚙️ Configuration
│   ├── config_payment.php                # Config webhook (secret, IP whitelist)
│   ├── db.php                            # Kết nối database
│   ├── example_config_payment.php        # Template config
│   └── example_db.php                    # Template DB config
│
├── 🗄️ Database
│   └── database_schema.sql               # Schema MySQL (tables, indexes)
│
├── 🧪 Testing & Development
│   ├── test_webhook.php                  # Test suite tự động
│   ├── create_test_transaction.php       # Tạo transaction test
│   └── webhook_history.php               # Admin panel xem logs
│
├── 📚 Documentation
│   ├── README.md                         # Tổng quan project
│   ├── QUICKSTART.md                     # Hướng dẫn 5 phút
│   ├── SETUP_GUIDE.md                    # Setup chi tiết
│   ├── INTEGRATION_GUIDE.md              # Tích hợp các service
│   ├── README_PAYMENT_WEBHOOK.md         # Technical docs
│   ├── FAQ.md                            # 30+ câu hỏi thường gặp
│   ├── CHANGELOG.md                      # Lịch sử thay đổi
│   └── FILE_STRUCTURE.md                 # File này
│
├── 📝 Logs
│   └── logs/
│       └── payment_webhook.log           # Log file (auto-generated)
│
├── 🔒 Security
│   ├── .gitignore                        # Ignore sensitive files
│   └── LICENSE                           # MIT License
│
└── 🎨 Frontend Assets (Optional)
    └── css/
        └── bootstrap/
            └── deposit.css               # CSS cho trang deposit
```

---

## 📝 Chi Tiết Từng File

### 🔥 Core API Files

#### `api_payment_webhook.php` ⭐ QUAN TRỌNG
**Mục đích:** API chính nhận webhook từ ngân hàng/service  
**Port:** Bất kỳ (thường 80/443)  
**Request:** POST với JSON payload  
**Response:** JSON `{"success": true/false, "message": "..."}`  

**Flow:**
1. Nhận POST request
2. Validate IP whitelist
3. Verify signature (nếu có)
4. Parse JSON payload
5. Extract unique_code (TS12345)
6. Find transaction trong DB
7. Check số tiền khớp
8. Update status → success
9. Cộng tiền vào balance
10. Return response

**Dùng khi:**
- Production webhook endpoint
- Tự động xử lý thanh toán

**Không dùng khi:**
- Test local (dùng test_webhook.php)

---

#### `api_payment_webhook_v2.php`
**Mục đích:** Version nâng cao có log vào DB  
**Khác biệt với v1:**
- Log mọi request vào bảng `webhook_logs`
- Lưu payload, response, IP, timestamp
- Admin có thể xem trong `webhook_history.php`

**Dùng khi:**
- Cần audit trail đầy đủ
- Debug/troubleshooting
- Compliance requirements

---

#### `check_transaction_status.php`
**Mục đích:** API AJAX kiểm tra trạng thái giao dịch  
**Request:** GET `?code=TS12345`  
**Response:** 
```json
{
  "success": true,
  "transaction_id": 123,
  "amount": 100000,
  "status": "success",
  "date": "10:00:00 01/01/2024",
  "code": "TS12345"
}
```

**Dùng trong:** `deposit.php` - Button "Xem lại trạng thái"

---

#### `check_balance.php`
**Mục đích:** API AJAX kiểm tra số dư user  
**Request:** GET (no params)  
**Response:** 
```json
{
  "success": true,
  "balance": 100000.00
}
```

**Dùng trong:** `deposit.php` - Auto-refresh mỗi 10s

---

#### `payment.php`
**Mục đích:** Xử lý mua gói dịch vụ  
**Request:** GET `?package_id=1&server=SG1&period=3`  
**Flow:**
1. Validate user logged in
2. Get package info
3. Check balance đủ không
4. Transaction:
   - Trừ balance
   - Insert transaction
   - Insert user_services
   - Commit
5. Send email kích hoạt
6. Redirect → manage_services.php

**Features:**
- Transaction-safe
- Email notification
- PHPMailer support
- Multiple payment periods (1,3,6,12,18,36 months)

---

#### `deposit.php`
**Mục đích:** Trang nạp tiền (frontend + backend)  
**Features:**
- Form nhập số tiền
- Hiển thị balance hiện tại
- Tạo giao dịch pending
- Hiển thị hướng dẫn chuyển khoản
- Lịch sử nạp tiền
- Lịch sử mua gói
- Auto-refresh balance (10s)
- Button check status
- Modal xem chi tiết GD

**CSRF Protection:** Có (session token)

---

### ⚙️ Configuration Files

#### `config_payment.php`
**QUAN TRỌNG:** File này chứa thông tin nhạy cảm!

```php
define('WEBHOOK_SECRET_KEY', 'xxx');      // Secret để verify webhook
define('ALLOWED_IPS', [...]);             // IP whitelist
define('CHECK_IP_WHITELIST', true/false); // Bật/tắt check IP
define('WEBHOOK_LOG_FILE', '...');        // Đường dẫn log file
define('WEBHOOK_DEBUG', true/false);      // Debug mode
```

**⚠️ Security:**
- KHÔNG commit file này lên Git
- Thay đổi WEBHOOK_SECRET_KEY trong production
- Bật CHECK_IP_WHITELIST = true khi deploy

---

#### `db.php`
**Kết nối database:**

```php
define('DB_HOST', 'localhost');
define('DB_USER', 'username');
define('DB_PASS', 'password');
define('DB_NAME', 'database');

$conn = new mysqli(...);
$conn->set_charset('utf8mb4');
$conn->query("SET time_zone = '+07:00'");
```

**⚠️ Security:**
- KHÔNG commit file này lên Git
- Dùng user DB có quyền hạn chế
- Enable SSL connection nếu DB remote

---

### 🗄️ Database

#### `database_schema.sql`
**Schema đầy đủ cho hệ thống:**

**Tables:**
1. `users` - Tài khoản người dùng
2. `transactions` - Giao dịch (nạp/mua)
3. `service_packages` - Danh sách gói dịch vụ
4. `user_services` - Gói đã mua
5. `receiving_accounts` - TK ngân hàng nhận tiền
6. `webhook_logs` - Log webhook (optional)

**Indexes:**
- `unique_code` (UNIQUE)
- `user_id` + `status`
- `transaction_date`

**Relations:**
- Foreign keys with CASCADE delete

---

### 🧪 Testing Files

#### `test_webhook.php`
**Automated test suite:**

```bash
php test_webhook.php
```

**Test cases:**
1. Giao dịch hợp lệ ✅
2. Mã viết thường (ts12345) ✅
3. Mã có khoảng trắng (TS 12345) ✅
4. Không có mã ❌ (expected)
5. Số tiền = 0 ❌ (expected)
6. Format Casso ✅

**Output:** Pass/Fail cho từng test

---

#### `create_test_transaction.php`
**Tạo transactions test trong DB:**

```bash
php create_test_transaction.php
```

**Tạo:**
- 5 transactions với status='pending'
- Codes: TS12345, TS67890, TS11111, TS22222, TS99999
- Amounts: 100k, 50k, 200k, 150k, 75k

**Dùng trước khi:** Chạy `test_webhook.php`

---

#### `webhook_history.php`
**Admin panel - Xem lịch sử webhook**

**Features:**
- List tất cả requests nhận được
- Show payload, response, IP, time
- Pagination (50 items/page)
- Filter by status
- Clear all logs

**⚠️ Access control:**
```php
if (!$_SESSION['is_admin']) die('Access denied');
```

---

### 📚 Documentation Files

| File | Nội dung | Độ dài |
|------|----------|--------|
| `README.md` | Overview, features, quick links | ~200 dòng |
| `QUICKSTART.md` | Chạy được trong 5 phút | ~300 dòng |
| `SETUP_GUIDE.md` | Setup chi tiết từng bước | ~500 dòng |
| `INTEGRATION_GUIDE.md` | Tích hợp Casso/VietQR/Sepay | ~600 dòng |
| `README_PAYMENT_WEBHOOK.md` | Technical deep dive | ~400 dòng |
| `FAQ.md` | 30+ câu hỏi thường gặp | ~400 dòng |
| `CHANGELOG.md` | Version history | ~100 dòng |
| `FILE_STRUCTURE.md` | File này | ~500 dòng |

---

## 🔄 Flow Diagram

### Deposit Flow:
```
User → deposit.php → Form submit → Create transaction (pending)
  ↓
User → Bank transfer (TS12345)
  ↓
Bank → Casso/VietQR → api_payment_webhook.php
  ↓
Parse code → Find transaction → Update status → Add balance
  ↓
User → deposit.php (auto refresh) → See updated balance ✅
```

### Payment Flow:
```
User → register_service.php → Select package & period
  ↓
payment.php → Check balance → Transaction (Deduct + Insert)
  ↓
Send email → Redirect to manage_services.php ✅
```

---

## 📊 File Size Estimates

| File | Size | Lines |
|------|------|-------|
| `api_payment_webhook.php` | ~15 KB | ~400 |
| `deposit.php` | ~20 KB | ~500 |
| `payment.php` | ~12 KB | ~300 |
| `database_schema.sql` | ~8 KB | ~200 |
| `test_webhook.php` | ~5 KB | ~150 |
| **Total** | **~200 KB** | **~5000** |

---

## 🔗 Dependencies

### PHP Extensions Required:
- `mysqli` - Database
- `json` - JSON parsing
- `session` - Session management
- `curl` - HTTP requests (optional, for testing)

### External Libraries (Optional):
- `PHPMailer` - Email sending (in payment.php)

### No Composer Required! ✅
Hệ thống chạy với PHP native, không cần Composer.

---

## 🚀 Deployment Checklist

**Trước khi deploy:**
- [ ] Copy `example_*.php` → `*.php`
- [ ] Điền thông tin trong config files
- [ ] Import `database_schema.sql`
- [ ] Tạo thư mục `logs/` với quyền 755
- [ ] Test local với `test_webhook.php`
- [ ] Đổi `CHECK_IP_WHITELIST = true`
- [ ] Cài SSL certificate
- [ ] Backup database

---

## 📞 Support

Cần giúp đỡ về cấu trúc file?  
- 📧 Email: support.vpn@vpnvietnam.com  
- 📱 Hotline: 0826.003.926

---

**Last updated:** 2025-01-01
