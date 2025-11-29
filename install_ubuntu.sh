#!/bin/bash

# ===================================================================
# VLESS Config Manager - Ubuntu VPS Auto Installer
# ===================================================================

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🚀 VLESS CONFIG MANAGER - UBUNTU VPS INSTALLER 🚀          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_warning "Khuyến nghị chạy với quyền root"
    echo "Run: sudo ./install_ubuntu.sh"
    echo ""
    read -p "Tiếp tục? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
print_info "Bắt đầu cài đặt..."
echo ""

# ===================================================================
# 1. UPDATE SYSTEM
# ===================================================================
print_info "Step 1/8: Update system..."
apt update -qq
apt upgrade -y -qq
print_success "System updated"

# ===================================================================
# 2. INSTALL PYTHON
# ===================================================================
print_info "Step 2/8: Installing Python 3..."
apt install -y python3 python3-pip python3-venv -qq
print_success "Python installed"
python3 --version

# ===================================================================
# 3. INSTALL DEPENDENCIES
# ===================================================================
print_info "Step 3/8: Installing Python packages..."
pip3 install -q streamlit requests pandas qrcode pillow
print_success "Dependencies installed"

# ===================================================================
# 4. CREATE DIRECTORY
# ===================================================================
print_info "Step 4/8: Creating app directory..."
INSTALL_DIR="/opt/vless-config-manager"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
print_success "Directory created: $INSTALL_DIR"

# ===================================================================
# 5. CHECK FILES
# ===================================================================
print_info "Step 5/8: Checking application files..."

if [ -f "vless_config_manager.py" ]; then
    print_success "App file found"
else
    print_warning "App file not found in current directory"
    print_info "Please copy vless_config_manager.py to $INSTALL_DIR"
    echo ""
    echo "Options:"
    echo "  1. scp vless_config_manager.py root@YOUR_VPS_IP:$INSTALL_DIR/"
    echo "  2. git clone YOUR_REPO $INSTALL_DIR"
    echo "  3. Copy manually"
    echo ""
    read -p "Have you copied the file? Press Enter when ready..."
fi

# ===================================================================
# 6. CREATE RUN SCRIPT
# ===================================================================
print_info "Step 6/8: Creating run script..."

cat > "$INSTALL_DIR/run.sh" << 'EOF'
#!/bin/bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
cd /opt/vless-config-manager
streamlit run vless_config_manager.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
EOF

chmod +x "$INSTALL_DIR/run.sh"
print_success "Run script created"

# ===================================================================
# 7. CREATE SYSTEMD SERVICE
# ===================================================================
print_info "Step 7/8: Creating systemd service..."

cat > /etc/systemd/system/vless-manager.service << EOF
[Unit]
Description=VLESS Config Manager
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/bin/bash $INSTALL_DIR/run.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vless-manager
print_success "Systemd service created"

# ===================================================================
# 8. CONFIGURE FIREWALL
# ===================================================================
print_info "Step 8/8: Configuring firewall..."

if command -v ufw &> /dev/null; then
    print_info "Configuring UFW..."
    ufw allow 8501/tcp
    ufw reload
    print_success "UFW configured (port 8501 opened)"
else
    print_warning "UFW not found, skipping firewall config"
    print_info "Manually open port 8501 if needed"
fi

# ===================================================================
# FINAL
# ===================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                  ✅ CÀI ĐẶT HOÀN TẤT!                           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

print_success "Installation completed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Installation Directory: $INSTALL_DIR"
echo "🔧 Service Name: vless-manager"
echo "🌐 Port: 8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. Start the service:"
echo "   sudo systemctl start vless-manager"
echo ""
echo "2. Check status:"
echo "   sudo systemctl status vless-manager"
echo ""
echo "3. Access the app:"
echo "   http://$(hostname -I | awk '{print $1}'):8501"
echo "   Or: http://YOUR_VPS_IP:8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 USEFUL COMMANDS:"
echo ""
echo "   Start:   sudo systemctl start vless-manager"
echo "   Stop:    sudo systemctl stop vless-manager"
echo "   Restart: sudo systemctl restart vless-manager"
echo "   Status:  sudo systemctl status vless-manager"
echo "   Logs:    sudo journalctl -u vless-manager -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get VPS IP
VPS_IP=$(hostname -I | awk '{print $1}')

echo "🌐 ACCESS URL:"
echo ""
echo "   http://$VPS_IP:8501"
echo ""

# Ask to start now
read -p "Start service now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting service..."
    systemctl start vless-manager
    sleep 3
    systemctl status vless-manager --no-pager
    echo ""
    print_success "Service started!"
    echo ""
    echo "Access now: http://$VPS_IP:8501"
fi

echo ""
print_success "Installation complete! 🎉"
echo ""
