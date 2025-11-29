#!/bin/bash

# VPN Auto Provisioning - Quick Start Script

echo "🚀 Starting VPN Auto Provisioning System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "⚙️  Please edit .env file with your configuration before running again."
    exit 1
fi

# Run the application
echo "✅ Starting server..."
echo "📄 API Documentation: http://localhost:8000/docs"
echo "📋 Health Check: http://localhost:8000/health"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
