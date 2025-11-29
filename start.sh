#!/bin/bash

# Script khởi động Admin Panel trên Ubuntu

echo "============================================"
echo "  VPN Vietnam - Admin Panel"
echo "  Đang khởi động trên Ubuntu..."
echo "============================================"
echo ""

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "⚠️  Lỗi: File .env không tồn tại!"
    echo "Vui lòng tạo file .env từ .env.example"
    exit 1
fi

# Lấy địa chỉ IP của server
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "📍 Server IP: $SERVER_IP"
echo "🚀 Đang khởi động Admin Panel..."
echo ""
echo "Truy cập tại: http://$SERVER_IP:5000"
echo "Email: admin@vpnvietnam.com"
echo "Password: Vpnvietnam123@!"
echo ""
echo "Nhấn Ctrl+C để dừng server"
echo "============================================"
echo ""

# Chạy ứng dụng
python3 admin_panel.py
