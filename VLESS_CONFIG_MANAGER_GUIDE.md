

# 🔐 VLESS CONFIG MANAGER - Complete Guide

## 🎯 Overview

**VLESS Config Manager** là tool quản lý VLESS configs **HOÀN TOÀN STANDALONE** - Không cần 3X-UI, không cần panel nào khác!

### ✨ Key Features

1. ✅ **Tạo VLESS Configs** - Đầy đủ options
2. ✅ **Support All Networks** - TCP, WebSocket, gRPC, HTTP/2
3. ✅ **Path-Based Configs** - WebSocket paths, HTTP paths
4. ✅ **Security Options** - None, TLS, REALITY
5. ✅ **Multi-User Management** - Quản lý nhiều users
6. ✅ **QR Code Generation** - Tự động generate QR
7. ✅ **Template System** - Pre-defined configs
8. ✅ **Backup/Restore** - Export/Import configs
9. ✅ **Statistics** - Analytics & insights
10. ✅ **Search & Filter** - Tìm configs nhanh

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install dependencies (if not installed)
pip3 install streamlit qrcode pillow pandas

# 2. Run app
./run_config_manager.sh

# Or
streamlit run vless_config_manager.py
```

### App opens at: `http://localhost:8501`

---

## 📋 Menu Structure

```
🔐 VLESS Config Manager
├── ➕ Tạo Config
│   ├── Basic Info
│   ├── Network Config
│   ├── Security Settings
│   └── Templates
│
├── 📋 Danh Sách Config
│   ├── Search & Filter
│   ├── Bulk Actions
│   └── Individual Actions
│
├── 📦 Templates
│   └── Pre-defined configs
│
├── 💾 Backup/Restore
│   ├── Backup (JSON/TXT)
│   └── Restore
│
└── 📊 Statistics
    ├── Overview
    └── Charts
```

---

## 🎨 Features Detail

### 1. ➕ Tạo Config

#### Basic Info

**Required Fields:**
- 📛 **Tên Config** - Unique identifier
- 🌐 **Server Address** - Domain hoặc IP
- 🔌 **Port** - 1-65535
- 🔑 **UUID** - Auto-generated hoặc custom

**Optional Fields:**
- ⏰ **Thời hạn** - Expiry date (days)
- 💾 **Data Limit** - Traffic limit (GB)

**Example:**
```
Tên: Client-VIP-001
Server: example.com
Port: 443
UUID: auto-generated
Thời hạn: 30 ngày
Data Limit: 100 GB
```

#### Network Config

##### 🔧 **TCP (Transmission Control Protocol)**

**Use Case:** Simple, direct connection

**Options:**
- **Header Type:**
  - `none` - Direct TCP
  - `http` - TCP with HTTP header (camouflage)

**Example Config:**
```json
{
  "network": "tcp",
  "security": "tls"
}
```

**Best for:**
- Direct connections
- High performance
- Low latency

---

##### 🌐 **WebSocket (WS)**

**Use Case:** CDN-friendly, bypass firewalls

**Options:**
- **Path** - WebSocket path (VD: `/vmess`, `/vless`)
- **Host** - Host header (optional)

**Example Config:**
```json
{
  "network": "ws",
  "ws_path": "/vmess",
  "ws_host": "example.com",
  "security": "tls"
}
```

**Best for:**
- Cloudflare CDN
- Bypass DPI (Deep Packet Inspection)
- Hide behind HTTPS

**Tips:**
- Port 443 cho TLS
- Port 80 hoặc 8080 cho non-TLS
- Path nên unique (không dùng `/`, `/ws`)

---

##### 📡 **gRPC (Google Remote Procedure Call)**

**Use Case:** Modern, efficient

**Options:**
- **Service Name** - gRPC service name
- **Mode:**
  - `gun` - gRPC over HTTP/2 (recommended)
  - `multi` - Multi-path mode

**Example Config:**
```json
{
  "network": "grpc",
  "grpc_service": "GunService",
  "grpc_mode": "gun",
  "security": "tls"
}
```

**Best for:**
- High performance
- Low detection
- HTTP/2 multiplexing

**Tips:**
- Requires TLS for production
- Service name nên unique

---

##### 🔗 **HTTP/2**

**Use Case:** Modern HTTP protocol

**Options:**
- **Path** - HTTP path
- **Host** - Host header

**Example Config:**
```json
{
  "network": "http",
  "http_path": "/path",
  "http_host": "example.com",
  "security": "tls"
}
```

**Best for:**
- Modern browsers
- HTTP/2 benefits
- Multiplexing

---

#### Security Settings

##### 🔓 **None (No Encryption)**

**Use Case:** Internal network, testing

**Pros:**
- Fast
- No overhead

**Cons:**
- ❌ No encryption
- ❌ Not secure
- ❌ Only for internal use

---

##### 🔒 **TLS (Transport Layer Security)**

**Use Case:** Standard encryption

**Options:**
- **SNI** - Server Name Indication (domain)
- **ALPN** - Application-Layer Protocol Negotiation
  - Common: `h2,http/1.1`
- **Fingerprint** - TLS fingerprint simulation
  - Options: chrome, firefox, safari, ios, android, edge
- **Allow Insecure** - Skip certificate verification (⚠️ not recommended)

**Example Config:**
```json
{
  "security": "tls",
  "tls_sni": "example.com",
  "tls_alpn": "h2,http/1.1",
  "tls_fingerprint": "chrome"
}
```

**Best for:**
- Standard encryption
- Wide compatibility
- CDN support

**Tips:**
- SNI phải match server certificate
- ALPN tùy thuộc vào server support
- Fingerprint giúp evade detection

---

##### 🛡️ **REALITY**

**Use Case:** Ultimate stealth

**Options:**
- **Public Key** - REALITY public key
- **Short ID** - Short identifier
- **Spider X** - Spider path
- **Flow** - XTLS flow control
  - `xtls-rprx-vision`
  - `xtls-rprx-vision-udp443`

**Example Config:**
```json
{
  "security": "reality",
  "reality_public_key": "...",
  "reality_short_id": "...",
  "reality_spider_x": "/",
  "flow": "xtls-rprx-vision"
}
```

**Best for:**
- Maximum stealth
- Anti-censorship
- High performance

**Requirements:**
- Server must support REALITY
- Proper key configuration

---

### 2. 📋 Danh Sách Config

#### Search & Filter

**Search by:**
- Remark (name)
- Server address
- UUID

**Filter by:**
- Network type
- Security type

#### Bulk Actions

- ☑️ **Select Multiple** - Checkbox selection
- 🗑️ **Bulk Delete** - Delete multiple configs

#### Individual Actions

For each config:
- 📱 **View QR Code** - Generate & display QR
- 📄 **Export JSON** - Export single config
- 📋 **Copy Link** - Copy VLESS link
- ⏸️/▶️ **Toggle Enable** - Enable/Disable
- 🗑️ **Delete** - Remove config

#### Config Info Display

Each config shows:
- 📛 Remark
- 🌐 Server:Port
- 🔑 UUID
- 🔧 Network type
- 🔒 Security type
- ⏰ Expiry status
- 💾 Data usage
- 📅 Created date
- 🔘 Enable/Disable status

---

### 3. 📦 Templates

Pre-defined configs for common use cases:

#### 🌟 **VLESS + TCP + REALITY**

```json
{
  "network": "tcp",
  "security": "reality",
  "flow": "xtls-rprx-vision"
}
```

**Best for:** Maximum stealth & performance

---

#### 🌐 **VLESS + WebSocket + TLS**

```json
{
  "network": "ws",
  "security": "tls",
  "ws_path": "/"
}
```

**Best for:** CDN (Cloudflare) + Bypass DPI

---

#### 📡 **VLESS + gRPC + TLS**

```json
{
  "network": "grpc",
  "security": "tls",
  "grpc_service": "grpcService"
}
```

**Best for:** Modern, efficient, low detection

---

### 4. 💾 Backup/Restore

#### Backup Options

**1. JSON Format**
- Full config data
- Structured
- Easy to edit

**2. TXT Format (Links Only)**
- VLESS links only
- One per line
- Easy to share

#### Restore Options

**1. Upload File**
- Drag & drop JSON file
- Validates before restore

**2. Paste JSON**
- Copy/paste JSON text
- Validates before restore

⚠️ **Warning:** Restore overwrites all current configs!

---

### 5. 📊 Statistics

#### Overview Metrics

- 📊 **Total Configs** - Total number
- 🟢 **Enabled** - Active configs
- 🔴 **Expired** - Past expiry date
- 💾 **Total Data Used** - Sum of all usage

#### Charts

- **Network Distribution** - Bar chart by network type
- **Security Distribution** - Bar chart by security type

#### Recent Configs

- Shows last 5 created configs

---

## 🎯 Use Cases & Examples

### Use Case 1: Cloudflare CDN Setup

**Goal:** Hide VPN traffic behind Cloudflare CDN

**Config:**
```
Network: WebSocket
Security: TLS
Server: your-domain.com (Cloudflare DNS)
Port: 443
WS Path: /vmess (unique path)
TLS SNI: your-domain.com
```

**Why it works:**
- Traffic looks like HTTPS
- Cloudflare hides real server IP
- WebSocket supports binary data
- Port 443 = Standard HTTPS

---

### Use Case 2: Maximum Stealth (REALITY)

**Goal:** Avoid detection & blocking

**Config:**
```
Network: TCP
Security: REALITY
Flow: xtls-rprx-vision
Reality Public Key: (from server)
Reality Short ID: (from server)
```

**Why it works:**
- REALITY mimics real TLS
- No detectable patterns
- High performance with XTLS
- Resistant to active probing

---

### Use Case 3: High Performance (gRPC)

**Goal:** Low latency, high throughput

**Config:**
```
Network: gRPC
Security: TLS
gRPC Service: GunService
gRPC Mode: gun
```

**Why it works:**
- HTTP/2 multiplexing
- Efficient binary protocol
- Low overhead
- Native browser support

---

### Use Case 4: Path-Based Multi-User

**Goal:** Multiple users with different paths

**Configs:**
```
User 1:
  Network: ws
  Path: /user1

User 2:
  Network: ws
  Path: /user2

User 3:
  Network: ws
  Path: /user3
```

**Benefits:**
- Easy identification
- Different routes
- Simple management

---

## 💡 Best Practices

### Security

1. ✅ **Always use TLS/REALITY** for production
2. ✅ **Use strong, random UUIDs**
3. ✅ **Set expiry dates** for temporary users
4. ✅ **Monitor data usage** to detect abuse
5. ✅ **Use unique paths** for WebSocket
6. ✅ **Enable only when needed** - disable unused configs

### Performance

1. ⚡ **gRPC** for best performance
2. ⚡ **TCP + REALITY** for balanced stealth/speed
3. ⚡ **Avoid nested proxies** when possible
4. ⚡ **Use CDN** only when necessary (adds latency)

### Management

1. 📋 **Use descriptive names** (VD: Client-VIP-001)
2. 📋 **Set data limits** to control usage
3. 📋 **Regular backups** - Export configs weekly
4. 📋 **Clean up expired** configs periodically
5. 📋 **Use templates** for consistency

---

## 🔧 Technical Details

### VLESS Link Format

```
vless://UUID@SERVER:PORT?params#REMARK
```

**Params include:**
- `security` - none/tls/reality
- `type` - tcp/ws/grpc/http
- `encryption` - none (VLESS only supports none)
- Network-specific params (path, serviceName, etc.)
- TLS-specific params (sni, alpn, fp, etc.)

### Config Storage

Configs stored in `vless_configs.json`:

```json
[
  {
    "id": "uuid",
    "remark": "name",
    "server": "example.com",
    "port": 443,
    "uuid": "uuid-here",
    "network": "ws",
    "security": "tls",
    ...
  }
]
```

---

## 🎓 Advanced Topics

### Custom Paths Strategy

**For WebSocket:**

Good paths:
- `/api/v1/ws`
- `/static/js/bundle.js`
- `/cdn-cgi/trace`
- `/analytics`

Bad paths:
- `/` (too obvious)
- `/ws` (too obvious)
- `/proxy` (too obvious)

**Tip:** Make it look like a real website resource!

---

### Multi-Port Strategy

**For same server:**

```
User 1: Port 443 (HTTPS)
User 2: Port 8443 (Alt HTTPS)
User 3: Port 2053 (Cloudflare)
User 4: Port 2083 (Cloudflare)
```

**Benefits:**
- Load balancing
- Redundancy
- Bypass port-specific blocking

---

### REALITY Configuration

**Server-side requirements:**
1. Xray-core with REALITY support
2. Valid destination website (dest)
3. Generated private/public key pair
4. Short IDs configured

**Client-side (this tool) needs:**
- Public key from server
- Short ID from server
- Dest address (optional, for routing)

---

## 🐛 Troubleshooting

### Issue: "Connection failed"

**Check:**
1. Server is running
2. Port is open (firewall)
3. Server config matches client config
4. TLS certificate is valid (for TLS)

---

### Issue: "QR code not working"

**Solutions:**
1. Re-generate link
2. Check link format
3. Try different QR scanner
4. Manually input config

---

### Issue: "CDN not working"

**Check:**
1. Using WebSocket (not TCP)
2. Port is 80, 443, 2053, 2083, 2087, 2096, 8080, or 8880
3. TLS enabled
4. Cloudflare DNS is set (orange cloud)

---

## 📚 Resources

### Official Docs

- **Xray-core:** https://xtls.github.io/
- **V2Ray:** https://www.v2ray.com/
- **VLESS Spec:** https://github.com/XTLS/Xray-core/discussions/716

### Community

- **Telegram:** (various VLESS groups)
- **GitHub Issues:** Xray-core repo

---

## 🎯 Roadmap

**Planned features:**

- [ ] VMess config support
- [ ] Trojan config support
- [ ] Config validation
- [ ] Traffic simulation
- [ ] Auto-renewal
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Mobile app

---

## ✅ Summary

**VLESS Config Manager** provides:

✅ **Complete standalone solution** - No panel dependency  
✅ **All network types** - TCP, WS, gRPC, HTTP/2  
✅ **Path-based configs** - Full path customization  
✅ **Security options** - None, TLS, REALITY  
✅ **User management** - Multi-user support  
✅ **Templates** - Quick config creation  
✅ **Backup/Restore** - Data safety  
✅ **Statistics** - Usage insights  

**Perfect for:**
- VPN providers
- Personal use
- Testing configs
- Learning VLESS

---

**Version:** 1.0  
**Date:** 2024  
**Status:** ✅ Production Ready

🔐 **MANAGE YOUR VLESS CONFIGS WITH EASE!** 🔐
