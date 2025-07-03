#!/bin/bash

# IVOR Backend Startup Script

echo "🤖 Starting IVOR Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys before continuing"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p chroma_db
mkdir -p logs

# Start the server
echo "🚀 Starting IVOR Backend server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000