#!/bin/bash

# IVOR Setup Script
# Automatically configures development environment

set -e

echo "🤖 IVOR Setup Script"
echo "===================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "✅ Python $PYTHON_VERSION (compatible)"
else
    echo "❌ Python 3.11+ required, found $PYTHON_VERSION"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    DOCKER_AVAILABLE=true
else
    echo "⚠️  Docker not found (optional for development)"
    DOCKER_AVAILABLE=false
fi

# Check Git
if command -v git &> /dev/null; then
    echo "✅ Git found"
else
    echo "❌ Git is required but not installed"
    exit 1
fi

echo ""
echo "🔧 Setting up IVOR..."

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env with your API keys:"
    echo "   - DEEPSEEK_API_KEY (required)"
    echo "   - OPENAI_API_KEY (recommended)"
    echo "   - QWEN_API_KEY (optional)"
    echo ""
    echo "Get your keys from:"
    echo "   - DeepSeek: https://platform.deepseek.com"
    echo "   - OpenAI: https://platform.openai.com"
    echo "   - Qwen: https://dashscope.aliyuncs.com"
    echo ""
    read -p "Press Enter after you've added your API keys to .env..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p chroma_db
mkdir -p logs

# Test basic imports
echo "🧪 Testing Python dependencies..."
python3 -c "
try:
    import fastapi, chromadb, sentence_transformers
    print('✅ Core dependencies working')
except ImportError as e:
    print(f'❌ Dependency error: {e}')
    exit(1)
"

# Check API keys
echo "🔑 Validating environment configuration..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

deepseek_key = os.getenv('DEEPSEEK_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

if not deepseek_key:
    print('❌ DEEPSEEK_API_KEY not found in .env')
    exit(1)
else:
    print('✅ DEEPSEEK_API_KEY configured')

if not openai_key:
    print('⚠️  OPENAI_API_KEY not configured (optional but recommended)')
else:
    print('✅ OPENAI_API_KEY configured')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the backend: ./start.sh"
echo "2. Test the API: curl http://localhost:8000/health/"
echo "3. Send a test message: curl -X POST http://localhost:8000/chat/message -H 'Content-Type: application/json' -d '{\"message\": \"Hello IVOR!\"}'"
echo ""

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "Alternative - Start with Docker:"
    echo "cd ../deployment && docker-compose up --build"
    echo ""
fi

echo "📖 For more information, see:"
echo "   - README.md"
echo "   - docs/API.md"
echo "   - docs/DEPLOYMENT.md"