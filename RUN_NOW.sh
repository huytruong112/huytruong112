#!/bin/bash

# Script để chạy Admin Panel ngay lập tức

clear

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           VPN VIETNAM - ADMIN PANEL                       ║"
echo "║           Starting Server...                               ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Kiểm tra dependencies
echo "📦 Checking dependencies..."
python3 -c "import flask, requests, psutil, speedtest" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Some dependencies missing!"
    echo "Installing now..."
    pip3 install -r requirements.txt --user
fi

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file..."
    cp .env.example .env
fi

# Lấy IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ Ready to start!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📍 Server will be available at:"
echo ""
echo "   Local:    http://localhost:5000"
echo "   Network:  http://$SERVER_IP:5000"
echo ""
echo "📧 Login credentials:"
echo ""
echo "   Email:    admin@vpnvietnam.com"
echo "   Password: Vpnvietnam123@!"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Starting Admin Panel..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Chạy server
python3 admin_panel.py
