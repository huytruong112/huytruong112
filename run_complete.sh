#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║   VPN Admin Pro - Multi-Server Complete Edition       ║"
echo "║   ✅ FIX: Thêm được nhiều server                      ║"
echo "║   ✅ Hỗ trợ: URL có Secret Path                       ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check file
if [ ! -f "vpn_admin_multiserver_complete.py" ]; then
    echo "❌ File không tồn tại!"
    exit 1
fi

# Install deps
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

echo "✅ Ready!"
echo ""
echo "🚀 Starting Multi-Server Complete Edition..."
echo ""
echo "✨ Tính năng:"
echo "   ✅ Thêm NHIỀU server khác nhau"
echo "   ✅ Hỗ trợ URL chuẩn: http://IP:PORT"
echo "   ✅ Hỗ trợ Secret Path: http://IP:PORT/PATH"
echo "   ✅ Auto parse & preview"
echo "   ✅ Test connection trước khi thêm"
echo ""
echo "📡 Truy cập: http://localhost:8501"
echo ""
echo "Nhấn Ctrl+C để dừng"
echo "════════════════════════════════════════════════════════"
echo ""

streamlit run vpn_admin_multiserver_complete.py --server.port 8501 --server.address 0.0.0.0
