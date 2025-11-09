#!/bin/bash
# Startup script for AI Recipe GenAI application

set -e

echo "🚀 Starting AI Recipe GenAI Application..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running."
    echo "   Please start Docker with: sudo systemctl start docker"
    echo "   Or add your user to the docker group to run without sudo:"
    echo "   sudo usermod -aG docker $USER"
    echo "   (then log out and back in)"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if .env file exists and has API key
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

if grep -q "your-api-key-here" .env; then
    echo "⚠️  WARNING: GOOGLE_API_KEY is set to 'your-api-key-here'"
    echo "   Please update .env with your actual Google API key"
    echo "   Get one from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start services
echo "📦 Starting Docker services..."
docker compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Initialize database
echo "🗄️  Initializing database tables..."
docker compose exec -T api python -m backend.init_db

# Check health
echo ""
echo "🏥 Checking API health..."
sleep 2
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running!"
    echo ""
    echo "🎉 Application started successfully!"
    echo ""
    echo "📋 Access points:"
    echo "   - API Health: http://localhost:8000/health"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Frontend: Run 'cd frontend && python3 -m http.server 5173'"
    echo "              Then open: http://localhost:5173/diagnosis.html"
    echo ""
    echo "📊 Useful commands:"
    echo "   - View logs: docker compose logs -f api"
    echo "   - Stop services: docker compose down"
    echo "   - Restart: docker compose restart"
else
    echo "⚠️  API health check failed. Check logs with: docker compose logs api"
fi

