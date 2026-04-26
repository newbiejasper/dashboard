#!/bin/bash
# DDYL BI Platform - Full Stack Startup
# 同时启动后端和前端

echo "🚀 DDYL BI Platform - 人人可用的数据可视化神器"
echo "================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start backend in background
echo "📡 Starting backend..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -q
python run.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Start frontend
echo "🎨 Starting frontend..."
cd "$SCRIPT_DIR/frontend"
npm install --silent 2>/dev/null
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ DDYL is running!"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C to kill both
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
