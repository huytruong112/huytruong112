#!/bin/bash

# VPN Admin Pro Multi-Server v2.0 - Secret Path Support

echo "══════════════════════════════════════════════════════"
echo "  VPN Admin Pro Multi-Server v2.0"
echo "  🔐 Hỗ trợ Secret Path"
echo "══════════════════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không tìm thấy!"
    exit 1
fi

# Check file
if [ ! -f "vpn_admin_pro_multiserver_v2.py" ]; then
    echo "❌ File vpn_admin_pro_multiserver_v2.py không tồn tại!"
    exit 1
fi

# Install deps
echo "📦 Checking dependencies..."
pip3 install -r requirements.txt --quiet

echo "✅ Dependencies OK"
echo ""

# Get IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="localhost"
fi

echo "🚀 Đang khởi động Multi-Server v2..."
echo ""
echo "✨ TÍNH NĂNG MỚI:"
echo "   ✅ Hỗ trợ URL chuẩn: http://IP:PORT"
echo "   ✅ Hỗ trợ Secret Path: http://IP:PORT/SECRET"
echo "   ✅ Auto parse & preview"
echo ""
echo "📡 Truy cập:"
echo "   → http://$SERVER_IP:8501"
echo "   → http://localhost:8501"
echo ""
echo "📚 Hướng dẫn: SECRET_PATH_GUIDE.md"
echo ""
echo "Nhấn Ctrl+C để dừng"
echo "══════════════════════════════════════════════════════"
echo ""

# Run
streamlit run vpn_admin_pro_multiserver_v2.py --server.port 8501 --server.address 0.0.0.0
