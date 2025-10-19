#!/bin/bash

echo "🍇 Starting Fruit & Vegetable Cost Allocation System"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Start the server
echo "🚀 Starting the API server..."
echo "   API will be available at: http://localhost:8000"
echo "   Frontend: Open index.html in your browser"
echo "   Test script: python test_example.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 main.py
