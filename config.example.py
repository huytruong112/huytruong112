# VPN Admin Pro - Configuration Template
# Copy file này thành config.py và điền thông tin của bạn

# === 3X-UI Panel Connection ===
# Địa chỉ Panel (bao gồm http:// hoặc https://)
HOST = "http://YOUR_VPS_IP:8001"

# Thông tin đăng nhập Panel
USERNAME = "admin"
PASSWORD = "your_secure_password"

# === Optional Settings ===
# Timeout cho API requests (giây)
API_TIMEOUT = 5

# Port range cho user mới
PORT_MIN = 10000
PORT_MAX = 60000

# Số ngày gia hạn mặc định
DEFAULT_EXTEND_DAYS = 30

# Giới hạn số user tạo hàng loạt
MAX_BULK_CREATE = 50

# === Advanced Settings ===
# Bật/tắt debug mode
DEBUG_MODE = False

# Log file path
LOG_FILE = "vpn_admin.log"

# Cache TTL (giây)
CACHE_TTL = 300

# === Examples ===
# HOST = "http://74.81.55.39:8001"
# HOST = "https://vpn.example.com"
# USERNAME = "admin"
# PASSWORD = "MySecurePass123!"
