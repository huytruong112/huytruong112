#!/bin/bash

echo "=================================="
echo "VPN Subscription API Setup"
echo "=================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your panel information."
else
    echo ""
    echo "⚠️  .env file already exists. Skipping..."
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p qrcodes
mkdir -p data

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x scripts/*.sh
chmod +x scripts/*.py
chmod +x examples/*.py

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your panel information"
echo "2. Test connection: python scripts/test_connection.py"
echo "3. Run the application: python main.py"
echo "4. Visit http://localhost:8000/docs"
echo ""
