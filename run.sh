#!/bin/bash

# Admin Panel Run Script

echo "=========================================="
echo "  VPN Vietnam - Admin Panel"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
    echo "✅ Dependencies installed"
    echo ""
fi

# Start the application
echo "🚀 Starting Admin Panel..."
echo ""
python admin_panel.py

# Deactivate virtual environment on exit
deactivate
