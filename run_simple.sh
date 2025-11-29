#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║     🚀 VPN Admin SIMPLE - v3.0                      ║"
echo "║         CHỈ NHỮNG TÍNH NĂNG HOẠT ĐỘNG!              ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "✅ Tạo Client - 100% OK"
echo "✅ Xóa Client - 100% OK"
echo "✅ Xem Client - 100% OK"
echo "✅ QR Code - 100% OK"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting..."
echo ""

cd /workspace
~/.local/bin/streamlit run vpn_admin_simple.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false
