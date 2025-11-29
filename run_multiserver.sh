#!/bin/bash

# VPN Admin Pro Multi-Server - Quick Start Script

echo "=========================================="
echo "  VPN Admin Pro Multi-Server Edition"
echo "=========================================="
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy!"
    echo "Cài đặt: sudo apt install python3"
    exit 1
fi

# Kiểm tra pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 không được tìm thấy!"
    echo "Cài đặt: sudo apt install python3-pip"
    exit 1
fi

# Kiểm tra file chính
if [ ! -f "vpn_admin_pro_multiserver.py" ]; then
    echo "❌ File vpn_admin_pro_multiserver.py không tồn tại!"
    exit 1
fi

# Cài đặt dependencies
echo "📦 Kiểm tra dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Lỗi cài đặt dependencies!"
    exit 1
fi

echo "✅ Dependencies OK"
echo ""

# Kiểm tra file config
if [ ! -f "servers_config.json" ]; then
    echo "⚠️  File servers_config.json chưa có"
    echo "ℹ️  File này sẽ tự động tạo khi bạn thêm server đầu tiên"
    echo ""
fi

# Lấy IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="localhost"
fi

echo "🚀 Đang khởi động Multi-Server Dashboard..."
echo ""
echo "📡 Truy cập tại:"
echo "   → http://$SERVER_IP:8501"
echo "   → http://localhost:8501"
echo ""
echo "📚 Hướng dẫn: Đọc file MULTISERVER_GUIDE.md"
echo ""
echo "⚡ Tính năng:"
echo "   ✅ Quản lý NHIỀU server trong 1 giao diện"
echo "   ✅ Switch server dễ dàng"
echo "   ✅ Tổng quan toàn hệ thống"
echo "   ✅ Load balancing thủ công"
echo ""
echo "Nhấn Ctrl+C để dừng"
echo "=========================================="
echo ""

# Chạy Streamlit
streamlit run vpn_admin_pro_multiserver.py --server.port 8501 --server.address 0.0.0.0
