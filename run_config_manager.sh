#!/bin/bash

export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

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

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Find streamlit
if command -v streamlit &> /dev/null; then
    STREAMLIT_CMD="streamlit"
elif [ -f "$HOME/.local/bin/streamlit" ]; then
    STREAMLIT_CMD="$HOME/.local/bin/streamlit"
elif [ -f "/usr/local/bin/streamlit" ]; then
    STREAMLIT_CMD="/usr/local/bin/streamlit"
else
    echo "❌ Streamlit not found!"
    echo "Install: pip3 install streamlit"
    exit 1
fi

echo "Using: $STREAMLIT_CMD"
echo "Directory: $SCRIPT_DIR"
echo ""

# Run app
$STREAMLIT_CMD run vless_config_manager.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
