# 🔌 Hướng Dẫn Tích Hợp Webhook với Các Service

## 📋 Mục Lục

1. [Tích hợp Casso.vn](#1-casso-vietnam)
2. [Tích hợp VietQR](#2-vietqr)
3. [Tích hợp Sepay](#3-sepay)
4. [Tích hợp Banking API trực tiếp](#4-banking-api-trực-tiếp)
5. [Custom Integration](#5-custom-integration)

---

## 1. Casso Vietnam

### 📌 Giới thiệu
[Casso.vn](https://casso.vn) là dịch vụ kết nối với ngân hàng, tự động nhận thông báo khi có biến động số dư.

### ⚙️ Cấu hình

#### Bước 1: Đăng ký tài khoản
1. Truy cập [https://casso.vn/dang-ky](https://casso.vn/dang-ky)
2. Đăng ký tài khoản
3. Liên kết tài khoản ngân hàng

#### Bước 2: Lấy API Key
1. Đăng nhập → **Tài khoản** → **API**
2. Copy **API Key** và **Secure Token**

#### Bước 3: Cấu hình Webhook
1. Vào **Cài đặt** → **Webhook**
2. Nhập:
   - **URL:** `https://yourdomain.com/api_payment_webhook.php`
   - **Sự kiện:** Chọn "Có giao dịch mới"
   - **Secure Token:** (tự động điền)
3. **Test Webhook** → **Lưu**

#### Bước 4: Lấy IP Webhook
Casso sẽ gọi từ các IP sau (thêm vào `config_payment.php`):
```php
define('ALLOWED_IPS', [
    '113.161.84.0/24',  // IP range của Casso
    '103.74.120.0/24',
]);
```

### 📊 Format Payload Casso
```json
{
  "id": 123456,
  "tid": "FT21123456789",
  "description": "TS12345 NGUYEN VAN A chuyen khoan",
  "amount": 100000,
  "when": "2024-01-01 10:00:00",
  "bank_sub_acc_id": "12345",
  "subAccId": "12345"
}
```

### 🔧 Điều chỉnh code (nếu cần)

Mở `api_payment_webhook.php` và thêm:

```php
// Trong hàm parse data
if (isset($payload['tid'])) {
    // Casso format
    $data = [
        'transaction_id' => $payload['tid'],
        'amount' => $payload['amount'],
        'description' => $payload['description'],
        'date' => $payload['when']
    ];
}
```

### ✅ Test
```bash
curl -X POST https://yourdomain.com/api_payment_webhook.php \
  -H "Content-Type: application/json" \
  -d '{
    "id": 123456,
    "tid": "FT21123456789",
    "description": "TS12345 Test",
    "amount": 100000,
    "when": "2024-01-01 10:00:00"
  }'
```

---

## 2. VietQR

### 📌 Giới thiệu
[VietQR.io](https://vietqr.io) - Tạo mã QR thanh toán và nhận webhook khi thanh toán thành công.

### ⚙️ Cấu hình

#### Bước 1: Đăng ký
1. Truy cập [https://vietqr.io](https://vietqr.io)
2. Đăng ký tài khoản

#### Bước 2: Tạo API Key
1. Vào **Dashboard** → **API Keys**
2. Tạo key mới

#### Bước 3: Cấu hình Webhook
1. **Settings** → **Webhook**
2. Nhập URL: `https://yourdomain.com/api_payment_webhook.php`
3. Secret key: (copy vào `config_payment.php`)

### 📊 Format Payload VietQR
```json
{
  "data": {
    "orderId": "ORD123",
    "amount": 100000,
    "description": "TS12345 Thanh toan",
    "accountNumber": "1234567890",
    "reference": "FT123",
    "transactionDate": "2024-01-01 10:00:00",
    "virtualAccountName": "NGUYEN VAN A",
    "virtualAccountNumber": "9704123456789"
  }
}
```

### 🔧 Điều chỉnh code

```php
// Trong api_payment_webhook.php
if (isset($payload['data']) && isset($payload['data']['orderId'])) {
    // VietQR format
    $data = [
        'transaction_id' => $payload['data']['reference'] ?? $payload['data']['orderId'],
        'amount' => $payload['data']['amount'],
        'description' => $payload['data']['description'],
        'date' => $payload['data']['transactionDate']
    ];
}
```

---

## 3. Sepay

### 📌 Giới thiệu
[Sepay.vn](https://sepay.vn) - Cổng thanh toán tự động cho website.

### ⚙️ Cấu hình

#### Bước 1: Đăng ký
1. Truy cập [https://my.sepay.vn/register](https://my.sepay.vn/register)
2. Đăng ký và xác thực

#### Bước 2: Liên kết ngân hàng
1. **Tài khoản** → **Liên kết ngân hàng**
2. Nhập thông tin tài khoản

#### Bước 3: Cấu hình Webhook
1. **Cài đặt** → **API & Webhook**
2. URL: `https://yourdomain.com/api_payment_webhook.php`
3. Secret key: (lưu vào config)

### 📊 Format Payload Sepay
```json
{
  "id": "TXN123456",
  "gateway": "SEPAY",
  "transaction_date": "2024-01-01 10:00:00",
  "account_number": "1234567890",
  "sub_account": "",
  "amount_in": 100000,
  "amount_out": 0,
  "accumulated": 5000000,
  "code": "FT123",
  "transaction_content": "TS12345 Nap tien",
  "reference_number": "REF123",
  "body": ""
}
```

### 🔧 Điều chỉnh code

```php
// Trong api_payment_webhook.php
if (isset($payload['gateway']) && $payload['gateway'] === 'SEPAY') {
    $data = [
        'transaction_id' => $payload['id'],
        'amount' => $payload['amount_in'],
        'description' => $payload['transaction_content'],
        'date' => $payload['transaction_date']
    ];
}
```

---

## 4. Banking API Trực Tiếp

### 📌 Các ngân hàng hỗ trợ API

- **VCB (Vietcombank)** - API cho doanh nghiệp
- **VPBank** - VPBank API Gateway
- **TPBank** - OpenAPI
- **ACB** - ACB API
- **Techcombank** - TCB API

### ⚙️ Yêu cầu

- Doanh nghiệp có tài khoản doanh nghiệp
- Đăng ký API Gateway với ngân hàng
- Nhận API credentials (Client ID, Secret)

### 📊 Format (ví dụ VPBank)

```json
{
  "transactionId": "VPB123456789",
  "amount": 100000,
  "description": "TS12345 GD thanh toan",
  "accountNumber": "1234567890",
  "transactionDate": "2024-01-01T10:00:00Z",
  "bankName": "VPBANK",
  "status": "SUCCESS"
}
```

### 🔧 Cách thức hoạt động

1. **Webhook:** Ngân hàng gọi webhook khi có GD
2. **Polling:** Định kỳ query API để lấy GD mới (cron job)

---

## 5. Custom Integration

### 📌 Tự xây dựng hệ thống

Nếu không dùng service trung gian, bạn có thể:

#### Option A: Email Parsing

1. Ngân hàng gửi email thông báo GD
2. Cron job đọc email (IMAP)
3. Parse nội dung → gọi webhook

**File:** `email_parser_cron.php`

```php
<?php
// Kết nối IMAP
$mailbox = imap_open('{imap.gmail.com:993/imap/ssl}INBOX', 'email@gmail.com', 'password');
$emails = imap_search($mailbox, 'UNSEEN SUBJECT "bien dong so du"');

foreach ($emails as $email_id) {
    $body = imap_body($mailbox, $email_id);
    
    // Parse nội dung
    if (preg_match('/So tien: ([\d,]+)/', $body, $amount_match) &&
        preg_match('/Noi dung: (.+)/', $body, $content_match)) {
        
        $amount = (float)str_replace(',', '', $amount_match[1]);
        $content = trim($content_match[1]);
        
        // Gọi webhook local
        $ch = curl_init('http://localhost/api_payment_webhook.php');
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
            'amount' => $amount,
            'description' => $content,
            'transaction_id' => 'EMAIL-' . time()
        ]));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_exec($ch);
        
        // Mark as read
        imap_setflag_full($mailbox, $email_id, "\\Seen");
    }
}

imap_close($mailbox);
```

#### Option B: SMS Parsing (tương tự)

#### Option C: Manual Confirmation

Admin xác nhận thủ công qua trang admin.

---

## 🔐 Security Best Practices

### 1. Verify Signature

Mỗi service có cách verify khác nhau:

**Casso:**
```php
$secure_token = 'YOUR_CASSO_SECURE_TOKEN';
$signature = hash_hmac('sha256', json_encode($payload), $secure_token);
if ($signature !== $_SERVER['HTTP_X_SIGNATURE']) {
    die('Invalid signature');
}
```

**VietQR:**
```php
$secret = 'YOUR_VIETQR_SECRET';
$data = json_encode($payload['data']);
$signature = hash_hmac('sha256', $data, $secret);
if ($signature !== $payload['signature']) {
    die('Invalid signature');
}
```

### 2. IP Whitelist

Luôn enable trong production:

```php
define('CHECK_IP_WHITELIST', true);
define('ALLOWED_IPS', [
    '103.xxx.xxx.xxx', // Service IP
]);
```

### 3. Rate Limiting

Thêm vào `api_payment_webhook.php`:

```php
// Giới hạn 100 requests/phút từ 1 IP
$ip = $_SERVER['REMOTE_ADDR'];
$key = "webhook_rate_{$ip}";
$count = (int)apcu_fetch($key);
if ($count > 100) {
    json_response(['success' => false, 'message' => 'Rate limit exceeded'], 429);
}
apcu_store($key, $count + 1, 60);
```

### 4. HTTPS Only

```php
if (empty($_SERVER['HTTPS']) || $_SERVER['HTTPS'] === 'off') {
    json_response(['success' => false, 'message' => 'HTTPS required'], 403);
}
```

---

## 🧪 Testing với Postman

### Collection Import

Tạo file `postman_collection.json`:

```json
{
  "info": {
    "name": "Payment Webhook Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Test Casso Format",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"id\": 123456,\n  \"tid\": \"FT123\",\n  \"description\": \"TS12345 Test\",\n  \"amount\": 100000,\n  \"when\": \"2024-01-01 10:00:00\"\n}"
        },
        "url": "https://yourdomain.com/api_payment_webhook.php"
      }
    },
    {
      "name": "Test VietQR Format",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"data\": {\n    \"orderId\": \"ORD123\",\n    \"amount\": 100000,\n    \"description\": \"TS12345 Test\"\n  }\n}"
        },
        "url": "https://yourdomain.com/api_payment_webhook.php"
      }
    }
  ]
}
```

---

## 📊 Monitoring & Alerts

### 1. Telegram Bot Notification

```php
function send_telegram_alert(string $message): void {
    $bot_token = 'YOUR_BOT_TOKEN';
    $chat_id = 'YOUR_CHAT_ID';
    
    file_get_contents("https://api.telegram.org/bot{$bot_token}/sendMessage?" . http_build_query([
        'chat_id' => $chat_id,
        'text' => $message
    ]));
}

// Gọi khi có payment thành công
send_telegram_alert("💰 Nạp tiền thành công: {$amount} VND - User ID: {$user_id}");
```

### 2. Slack Webhook

```php
function send_slack_alert(string $message): void {
    $webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL';
    
    $ch = curl_init($webhook_url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['text' => $message]));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_exec($ch);
}
```

---

## 🎯 Tổng Kết

| Service | Độ khó | Chi phí | Tính năng |
|---------|--------|---------|-----------|
| **Casso** | ⭐ Dễ | ~200k/tháng | Webhook realtime, hỗ trợ nhiều NH |
| **VietQR** | ⭐⭐ TB | Free - 500k/tháng | QR động, webhook |
| **Sepay** | ⭐ Dễ | ~300k/tháng | Webhook, dashboard |
| **Banking API** | ⭐⭐⭐ Khó | Phí NH | Chính chủ, uy tín |
| **Email Parse** | ⭐⭐ TB | Free | Delay, cần cron |

### Khuyến nghị:

- **Startup/Cá nhân:** Dùng **Casso** hoặc **Sepay** (dễ setup)
- **Doanh nghiệp nhỏ:** **VietQR** + Casso (backup)
- **Doanh nghiệp lớn:** **Banking API** trực tiếp

---

## 📞 Hỗ Trợ

- Email: support.vpn@vpnvietnam.com
- Hotline: 0826.003.926
