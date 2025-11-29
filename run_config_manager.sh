#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║     🔐 VLESS CONFIG MANAGER v1.0                    ║"
echo "║         STANDALONE - KHÔNG CẦN PANEL!               ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "✨ Tính năng đầy đủ:"
echo "  ✅ Tạo VLESS configs (TCP/WS/gRPC/HTTP2)"
echo "  ✅ Support path-based configs"
echo "  ✅ Multi-user management"
echo "  ✅ QR Code generation"
echo "  ✅ Template system"
echo "  ✅ Backup/Restore"
echo "  ✅ Statistics"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting..."
echo ""

cd /workspace
~/.local/bin/streamlit run vless_config_manager.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false
