#!/bin/bash
# DDYL BI Platform - Development Startup Script
# 后端启动

echo "🚀 DDYL BI Platform - 人人可用的数据可视化神器"
echo "================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt -q

# Run backend
echo "✅ Starting backend on http://localhost:8000"
echo "📘 API docs at http://localhost:8000/docs"
echo ""
python run.py
