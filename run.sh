#!/bin/bash

# VPN Admin Pro - Quick Start Script
# Sử dụng: bash run.sh

echo "========================================"
echo "  VPN Admin Pro - Starting Dashboard"
echo "========================================"
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

# Kiểm tra requirements
if [ ! -f "requirements.txt" ]; then
    echo "❌ File requirements.txt không tồn tại!"
    exit 1
fi

# Kiểm tra main file
if [ ! -f "vpn_admin_pro.py" ]; then
    echo "❌ File vpn_admin_pro.py không tồn tại!"
    exit 1
fi

# Cài đặt dependencies nếu cần
echo "📦 Kiểm tra dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Lỗi cài đặt dependencies!"
    exit 1
fi

echo "✅ Dependencies OK"
echo ""

# Lấy IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="localhost"
fi

echo "🚀 Đang khởi động Dashboard..."
echo "📡 Truy cập tại: http://$SERVER_IP:8501"
echo "🔗 Hoặc: http://localhost:8501"
echo ""
echo "Nhấn Ctrl+C để dừng"
echo "========================================"
echo ""

# Chạy Streamlit
streamlit run vpn_admin_pro.py --server.port 8501 --server.address 0.0.0.0
