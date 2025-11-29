#!/bin/bash

# Deployment script for X-UI/3X-UI Manager
# Usage: ./deploy.sh

set -e

echo "🚀 Starting deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}⚠️  Please do not run as root${NC}"
    exit 1
fi

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Creating .env from .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
        echo -e "${YELLOW}   nano .env${NC}"
        read -p "Press Enter after you've configured .env..."
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

# Test database connection
echo -e "${YELLOW}Initializing database...${NC}"
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()" 2>&1
echo -e "${GREEN}✅ Database initialized${NC}"

# Test panel connection
echo -e "${YELLOW}Testing panel connection...${NC}"
python3 << EOF
import sys
from config import Config
from app.integrations.panel_manager import PanelManager

try:
    panel = PanelManager()
    inbounds = panel.get_inbounds()
    if inbounds:
        print("${GREEN}✅ Panel connection successful${NC}")
        print(f"Found {len(inbounds)} inbound(s)")
        sys.exit(0)
    else:
        print("${RED}❌ Cannot connect to panel${NC}")
        sys.exit(1)
except Exception as e:
    print(f"${RED}❌ Panel connection error: {e}${NC}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}⚠️  Panel connection failed. Please check your configuration in .env${NC}"
    echo -e "${YELLOW}   The application will still deploy, but panel features won't work.${NC}"
fi

# Ask for deployment type
echo ""
echo -e "${YELLOW}Select deployment type:${NC}"
echo "1) Development (python app.py)"
echo "2) Production with Gunicorn"
echo "3) Create systemd service"
echo "4) Exit"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo -e "${GREEN}🎉 Deployment complete!${NC}"
        echo -e "${YELLOW}Starting development server...${NC}"
        echo -e "${YELLOW}Access at: http://localhost:5000${NC}"
        python3 app.py
        ;;
    2)
        # Install gunicorn if not installed
        pip install gunicorn > /dev/null 2>&1
        echo -e "${GREEN}🎉 Deployment complete!${NC}"
        echo -e "${YELLOW}Starting production server with Gunicorn...${NC}"
        echo -e "${YELLOW}Access at: http://localhost:5000${NC}"
        gunicorn -w 4 -b 0.0.0.0:5000 app:app
        ;;
    3)
        echo -e "${YELLOW}Creating systemd service...${NC}"
        
        # Get current directory
        CURRENT_DIR=$(pwd)
        CURRENT_USER=$(whoami)
        
        # Create service file
        SERVICE_FILE="/tmp/xui-manager.service"
        cat > $SERVICE_FILE << SERVICEEOF
[Unit]
Description=X-UI/3X-UI Manager
After=network.target

[Service]
Type=notify
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF
        
        echo -e "${YELLOW}Service file created at: $SERVICE_FILE${NC}"
        echo ""
        echo -e "${YELLOW}To install the service, run these commands:${NC}"
        echo -e "  ${GREEN}sudo cp $SERVICE_FILE /etc/systemd/system/xui-manager.service${NC}"
        echo -e "  ${GREEN}sudo systemctl daemon-reload${NC}"
        echo -e "  ${GREEN}sudo systemctl enable xui-manager${NC}"
        echo -e "  ${GREEN}sudo systemctl start xui-manager${NC}"
        echo -e "  ${GREEN}sudo systemctl status xui-manager${NC}"
        echo ""
        echo -e "${GREEN}🎉 Deployment complete!${NC}"
        ;;
    4)
        echo -e "${GREEN}🎉 Deployment complete!${NC}"
        echo -e "${YELLOW}To start the application manually:${NC}"
        echo -e "  ${GREEN}source venv/bin/activate${NC}"
        echo -e "  ${GREEN}python3 app.py${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
