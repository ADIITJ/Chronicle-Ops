#!/bin/bash

# ChronicleOps Startup Script
# Starts both backend and frontend servers

set -e

echo "🚀 Starting ChronicleOps..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
DATABASE_URL="postgresql://chronicleops:dev_password_change_in_prod@localhost:5432/chronicleops"
REDIS_HOST="localhost"
OPENROUTER_API_KEY="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"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker is not running. Starting Docker Desktop...${NC}"
    open -a Docker
    echo "Waiting for Docker to start..."
    sleep 10
fi

# Start Docker containers
echo -e "${BLUE}📦 Starting Docker containers (PostgreSQL + Redis)...${NC}"
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Run database migrations
echo -e "${BLUE}🗄️  Running database migrations...${NC}"
cd backend
DATABASE_URL="$DATABASE_URL" /Users/ashishdate/Library/Python/3.13/bin/alembic upgrade head
cd ..

# Kill any existing processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "uvicorn api.gateway:app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
sleep 2

# Start backend
echo -e "${GREEN}🔧 Starting Backend API on port $BACKEND_PORT...${NC}"
cd backend
PYTHONPATH=/Users/ashishdate/Documents/Projects/company-simulation/backend \
DATABASE_URL="$DATABASE_URL" \
REDIS_HOST="$REDIS_HOST" \
OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m uvicorn api.gateway:app \
  --host 0.0.0.0 \
  --port $BACKEND_PORT \
  --reload > ../logs/backend.log 2>&1 &

BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may not be fully ready yet${NC}"
fi

# Start frontend
echo -e "${GREEN}🎨 Starting Frontend on port $FRONTEND_PORT...${NC}"
cd frontend
NEXT_PUBLIC_API_URL="http://localhost:$BACKEND_PORT" \
npx next dev -p $FRONTEND_PORT > ../logs/frontend.log 2>&1 &

FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
cd ..

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 10

echo ""
echo -e "${GREEN}✅ ChronicleOps is running!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 Backend API:${NC}  http://localhost:$BACKEND_PORT"
echo -e "${BLUE}🌐 Frontend UI:${NC}  http://localhost:$FRONTEND_PORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo "  Backend:  tail -f logs/backend.log"
echo "  Frontend: tail -f logs/frontend.log"
echo ""
echo -e "${YELLOW}🛑 To stop:${NC}"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  docker-compose down"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose down; echo 'Stopped.'; exit 0" INT

# Keep script running
wait
