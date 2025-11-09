#!/bin/bash
# Startup script that uses sudo for Docker commands

set -e

echo "🚀 Starting AI Recipe GenAI Application..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Check API key
if grep -q "your-api-key-here" .env; then
    echo "⚠️  WARNING: GOOGLE_API_KEY is set to 'your-api-key-here'"
    echo "   The app will start but LLM features won't work."
    echo "   Update .env with your actual API key from:"
    echo "   https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Docker
echo "📦 Checking Docker..."
if ! sudo docker info > /dev/null 2>&1; then
    echo "❌ Cannot connect to Docker daemon."
    echo "   Please ensure Docker is running: sudo systemctl start docker"
    exit 1
fi
echo "✅ Docker is accessible"
echo ""

# Start services
echo "📦 Starting Docker services..."
sudo docker compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 5

# Initialize database
echo "🗄️  Initializing database tables..."
sudo docker compose exec -T api python -m backend.init_db

# Check health
echo ""
echo "🏥 Checking API health..."
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running!"
    echo ""
    echo "🎉 Application started successfully!"
    echo ""
    echo "📋 Access points:"
    echo "   - API Health: http://localhost:8000/health"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Frontend: cd frontend && python3 -m http.server 5173"
    echo "              Then open: http://localhost:5173/diagnosis.html"
    echo ""
    echo "📊 Useful commands:"
    echo "   - View logs: sudo docker compose logs -f api"
    echo "   - Stop: sudo docker compose down"
    echo "   - Restart: sudo docker compose restart"
else
    echo "⚠️  API health check failed."
    echo "   Check logs with: sudo docker compose logs api"
    echo "   Or view all logs: sudo docker compose logs"
fi

