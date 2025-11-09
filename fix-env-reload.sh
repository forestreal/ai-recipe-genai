#!/bin/bash
# Fix environment variable loading in Docker container

cd "$(dirname "$0")"

echo "🔧 Fixing API key loading in Docker container..."
echo ""

# Verify .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

API_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d'=' -f2)
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-api-key-here" ]; then
    echo "❌ Error: GOOGLE_API_KEY not set in .env"
    exit 1
fi

echo "✅ Found API key in .env: ${API_KEY:0:20}..."
echo ""

# Stop the container
echo "1. Stopping API container..."
docker compose stop api 2>/dev/null || sudo docker compose stop api

# Remove the container (this forces recreation with new env vars)
echo "2. Removing API container (will recreate with new env vars)..."
docker compose rm -f api 2>/dev/null || sudo docker compose rm -f api

# Start the container (this will recreate it and load .env)
echo "3. Starting API container (recreating with .env)..."
docker compose up -d api 2>/dev/null || sudo docker compose up -d api

echo ""
echo "⏳ Waiting 15 seconds for API to start..."
sleep 15

echo ""
echo "4. Verifying API key is loaded..."
docker compose exec -T api python -c "
from backend.core.config import settings
if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY not in ['', 'your-api-key-here', 'None']:
    print(f'✅ API key loaded: {settings.GOOGLE_API_KEY[:20]}...')
else:
    print('❌ API key NOT loaded')
    exit(1)
" 2>/dev/null || sudo docker compose exec -T api python -c "
from backend.core.config import settings
if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY not in ['', 'your-api-key-here', 'None']:
    print(f'✅ API key loaded: {settings.GOOGLE_API_KEY[:20]}...')
else:
    print('❌ API key NOT loaded')
    exit(1)
"

echo ""
echo "5. Checking API logs..."
docker compose logs api --tail 10 | grep -E "(Gemini|API|key|initialized|✅|⚠️)" | tail -5 || sudo docker compose logs api --tail 10 | grep -E "(Gemini|API|key|initialized|✅|⚠️)" | tail -5

echo ""
echo "✅ Done! The API container has been recreated with the .env file."
echo ""
echo "📝 If the API key still isn't loading, try:"
echo "   - Check .env file has no extra spaces: GOOGLE_API_KEY=AIzaSy..."
echo "   - Make sure .env is in the same directory as docker-compose.yaml"
echo "   - Try: docker compose down && docker compose up -d"


