#!/bin/bash

# Purple Patch Farms - Deployment Script
echo "🍇 Purple Patch Farms - Cost Allocation Dashboard"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ Python and pip are installed"

# Navigate to backend directory
cd backend

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Start the application
echo "🚀 Starting Purple Patch Farms Dashboard..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📊 Dashboard: http://localhost:8000"
echo "🔧 API Docs: http://localhost:8000/api/docs"
echo "=" * 60

python3 app.py
