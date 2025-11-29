#!/bin/bash

# Enhanced start script with diagnostics

clear

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           VPN VIETNAM - ADMIN PANEL                       ║"
echo "║           Starting with diagnostics...                     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Stop any existing server
if pgrep -f "admin_panel.py" > /dev/null; then
    echo "⚠️  Stopping existing server..."
    pkill -f admin_panel.py
    sleep 2
fi

# Quick health check
echo "📋 Pre-flight checks:"
echo ""

# Check Python
python3 --version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Python: $(python3 --version)"
else
    echo "  ❌ Python not found"
    exit 1
fi

# Check modules
python3 -c "import flask, requests, psutil" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Dependencies: OK"
else
    echo "  ❌ Dependencies missing"
    exit 1
fi

# Check files
if [ -f "admin_panel.py" ]; then
    echo "  ✅ admin_panel.py: Found"
else
    echo "  ❌ admin_panel.py: Not found"
    exit 1
fi

if [ -d "templates" ] && [ $(ls templates/*.html 2>/dev/null | wc -l) -eq 7 ]; then
    echo "  ✅ Templates: 7 files"
else
    echo "  ❌ Templates: Missing"
    exit 1
fi

if [ -f "static/css/style.css" ]; then
    echo "  ✅ Static files: OK"
else
    echo "  ❌ Static files: Missing"
    exit 1
fi

# Get server info
SERVER_IP=$(hostname -I | awk '{print $1}')
PORT=5000

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Server will be accessible at:"
echo ""
echo "   📍 Local:   http://localhost:$PORT"
echo "   📍 Network: http://$SERVER_IP:$PORT"
echo ""
echo "🔐 Login credentials:"
echo ""
echo "   Email:    admin@vpnvietnam.com"
echo "   Password: Vpnvietnam123@!"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "💡 IMPORTANT - If you see blank page:"
echo ""
echo "   1. Clear browser cache (Ctrl+Shift+Delete)"
echo "   2. Try Incognito/Private mode"
echo "   3. Check browser console (F12) for errors"
echo "   4. Make sure you're using the correct URL above"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Starting server..."
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Start the server
python3 admin_panel.py

# If server stops
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Server stopped"
echo "════════════════════════════════════════════════════════════"
