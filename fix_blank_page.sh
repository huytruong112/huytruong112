#!/bin/bash

# Script to diagnose and fix blank page issue

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           FIXING BLANK PAGE ISSUE                         ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Check if server is running
echo "1. Checking if server is running..."
if pgrep -f "admin_panel.py" > /dev/null; then
    echo "   ⚠️  Server is already running"
    echo "   PID: $(pgrep -f admin_panel.py)"
    echo "   Stopping it..."
    pkill -f admin_panel.py
    sleep 2
fi
echo "   ✅ Server stopped"
echo ""

# 2. Check templates
echo "2. Checking templates..."
if [ -d "templates" ]; then
    template_count=$(ls templates/*.html 2>/dev/null | wc -l)
    echo "   Templates found: $template_count"
    if [ $template_count -eq 7 ]; then
        echo "   ✅ All templates present"
    else
        echo "   ❌ Missing templates"
    fi
else
    echo "   ❌ Templates directory not found"
fi
echo ""

# 3. Check static files
echo "3. Checking static files..."
if [ -f "static/css/style.css" ]; then
    css_size=$(wc -c < static/css/style.css)
    echo "   ✅ CSS file: $css_size bytes"
else
    echo "   ❌ CSS file missing"
fi

if [ -f "static/js/main.js" ]; then
    js_size=$(wc -c < static/js/main.js)
    echo "   ✅ JS file: $js_size bytes"
else
    echo "   ❌ JS file missing"
fi
echo ""

# 4. Test template rendering
echo "4. Testing template rendering..."
python3 test_server.py
echo ""

# 5. Check browser cache
echo "5. Tips to fix blank page in browser:"
echo ""
echo "   If you see blank page in browser:"
echo ""
echo "   A. Clear browser cache:"
echo "      - Press Ctrl+Shift+Delete"
echo "      - Clear cached images and files"
echo "      - Or use Incognito/Private mode"
echo ""
echo "   B. Check browser console:"
echo "      - Press F12"
echo "      - Check Console tab for errors"
echo "      - Check Network tab for failed requests"
echo ""
echo "   C. Check correct URL:"
echo "      - Use: http://localhost:5000"
echo "      - Or: http://YOUR_SERVER_IP:5000"
echo ""
echo "   D. Make sure no firewall blocking:"
echo "      sudo ufw allow 5000/tcp"
echo ""

echo "════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Now try starting the server:"
echo "   python3 admin_panel.py"
echo ""
echo "Then open browser: http://localhost:5000"
echo ""
echo "════════════════════════════════════════════════════════════"
