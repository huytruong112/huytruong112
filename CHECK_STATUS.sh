#!/bin/bash

# Script kiểm tra trạng thái Admin Panel

echo "========================================"
echo "  KIỂM TRA TRẠNG THÁI ADMIN PANEL"
echo "========================================"
echo ""

# Kiểm tra Python
echo "🐍 Python Version:"
python3 --version
echo ""

# Kiểm tra dependencies
echo "📦 Checking Dependencies..."
python3 -c "
try:
    import flask
    import requests
    import psutil
    import speedtest
    print('✅ Flask: OK')
    print('✅ Requests: OK')
    print('✅ Psutil: OK')
    print('✅ Speedtest: OK')
except ImportError as e:
    print(f'❌ Missing: {e}')
"
echo ""

# Kiểm tra file cấu hình
echo "⚙️  Configuration Files:"
if [ -f ".env" ]; then
    echo "✅ .env: Exists"
else
    echo "❌ .env: Not found"
fi

if [ -f "admin_panel.py" ]; then
    echo "✅ admin_panel.py: Exists"
else
    echo "❌ admin_panel.py: Not found"
fi
echo ""

# Kiểm tra templates
echo "📄 Templates:"
if [ -d "templates" ]; then
    template_count=$(ls templates/*.html 2>/dev/null | wc -l)
    echo "✅ Templates directory: $template_count files"
else
    echo "❌ Templates directory: Not found"
fi
echo ""

# Kiểm tra static files
echo "🎨 Static Files:"
if [ -d "static" ]; then
    echo "✅ Static directory: Exists"
    if [ -f "static/css/style.css" ]; then
        echo "  ✅ CSS: Found"
    fi
    if [ -f "static/js/main.js" ]; then
        echo "  ✅ JavaScript: Found"
    fi
else
    echo "❌ Static directory: Not found"
fi
echo ""

# Kiểm tra port
echo "🔌 Port Status:"
if netstat -tulpn 2>/dev/null | grep -q ":5000"; then
    echo "⚠️  Port 5000: In use"
    echo "   Process: $(sudo lsof -i :5000 -t 2>/dev/null | head -1)"
else
    echo "✅ Port 5000: Available"
fi
echo ""

# Kiểm tra server IP
echo "🌐 Server Information:"
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo "Hostname: $(hostname)"
echo ""

# Kiểm tra xem admin_panel có đang chạy không
echo "🚀 Admin Panel Process:"
if pgrep -f "admin_panel.py" > /dev/null; then
    echo "✅ Admin Panel: RUNNING"
    echo "   PID: $(pgrep -f admin_panel.py)"
else
    echo "⚠️  Admin Panel: NOT RUNNING"
fi
echo ""

echo "========================================"
echo "  SUMMARY"
echo "========================================"

# Tổng kết
all_ok=true

python3 -c "import flask, requests, psutil, speedtest" 2>/dev/null || all_ok=false
[ -f ".env" ] || all_ok=false
[ -f "admin_panel.py" ] || all_ok=false
[ -d "templates" ] || all_ok=false
[ -d "static" ] || all_ok=false

if [ "$all_ok" = true ]; then
    echo "✅ Status: READY TO RUN"
    echo ""
    echo "To start the admin panel, run:"
    echo "  python3 admin_panel.py"
    echo ""
    echo "Or use the start script:"
    echo "  ./start.sh"
else
    echo "❌ Status: NOT READY"
    echo ""
    echo "Please check the errors above and fix them."
fi

echo "========================================"
