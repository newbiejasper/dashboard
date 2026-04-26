#!/bin/bash
# DDYL BI Platform - Frontend Startup
echo "🚀 DDYL Frontend Starting..."

cd "$(dirname "$0")"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required"
    exit 1
fi

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node dependencies..."
    npm install
fi

echo "✅ Starting frontend on http://localhost:5173"
npm run dev
