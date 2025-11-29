#!/bin/bash

# Script to fix speedtest module issue

echo "============================================"
echo "  Fixing Speedtest Module"
echo "============================================"
echo ""

echo "📦 Uninstalling old speedtest-cli..."
pip3 uninstall -y speedtest-cli 2>/dev/null

echo ""
echo "📦 Installing speedtest-cli properly..."
pip3 install --user speedtest-cli

echo ""
echo "🔍 Testing speedtest module..."
python3 << 'EOF'
try:
    import speedtest
    print("✅ Speedtest module works with: import speedtest")
except ImportError:
    try:
        from speedtest import Speedtest
        print("✅ Speedtest module works with: from speedtest import Speedtest")
    except ImportError:
        print("❌ Speedtest module still not working")
        print("Try: pip3 install --user --force-reinstall speedtest-cli")
EOF

echo ""
echo "============================================"
echo "  Done!"
echo "============================================"
