#!/bin/bash

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                      ║${NC}"
echo -e "${BLUE}║     🚀 VPN Admin Pro - Multi-Server Edition         ║${NC}"
echo -e "${BLUE}║           Version 2.3.3 - Debug Mode                ║${NC}"
echo -e "${BLUE}║                                                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Starting application...${NC}"
echo ""
echo -e "📍 App will open in browser: ${GREEN}http://localhost:8501${NC}"
echo ""
echo -e "${BLUE}🔍 Debug Mode: ACTIVE${NC}"
echo -e "   → Xem debug expanders để tìm lỗi chính xác!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run Streamlit
cd /workspace
~/.local/bin/streamlit run vpn_admin_pro_multiserver.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false
