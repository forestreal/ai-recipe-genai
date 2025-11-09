#!/bin/bash
# Force reload environment variables by recreating the container

cd "$(dirname "$0")"

echo "🔄 Force reloading environment variables..."
echo ""

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Verify API key is in .env
API_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d'=' -f2 | tr -d ' ')
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-api-key-here" ]; then
    echo "❌ Error: GOOGLE_API_KEY not set in .env"
    exit 1
fi

echo "✅ API key found in .env: ${API_KEY:0:20}..."
echo ""

# Stop and remove container to force recreation
echo "Stopping and removing API container..."
docker compose stop api 2>/dev/null || sudo docker compose stop api
docker compose rm -f api 2>/dev/null || sudo docker compose rm -f api

echo ""
echo "Recreating API container with fresh .env..."
docker compose up -d api 2>/dev/null || sudo docker compose up -d api

echo ""
echo "⏳ Waiting 15 seconds for API to start..."
sleep 15

echo ""
echo "Verifying API key is loaded..."
docker compose exec -T api python3 -c "
import os
from backend.core.config import settings
key = settings.GOOGLE_API_KEY
if key and key.strip() and key not in ['', 'your-api-key-here', 'None', 'null']:
    print(f'✅ SUCCESS: API key loaded: {key[:20]}...')
    print(f'   Full key length: {len(key)} characters')
else:
    print('❌ FAILED: API key not loaded')
    print(f'   Value: {repr(key)}')
    print('')
    print('Environment variables in container:')
    for k, v in os.environ.items():
        if 'GOOGLE' in k or 'GEMINI' in k:
            print(f'   {k}={v[:20] if v else \"(empty)\"}...')
    exit(1)
" 2>&1 || sudo docker compose exec -T api python3 -c "
import os
from backend.core.config import settings
key = settings.GOOGLE_API_KEY
if key and key.strip() and key not in ['', 'your-api-key-here', 'None', 'null']:
    print(f'✅ SUCCESS: API key loaded: {key[:20]}...')
    print(f'   Full key length: {len(key)} characters')
else:
    print('❌ FAILED: API key not loaded')
    print(f'   Value: {repr(key)}')
    print('')
    print('Environment variables in container:')
    for k, v in os.environ.items():
        if 'GOOGLE' in k or 'GEMINI' in k:
            print(f'   {k}={v[:20] if v else \"(empty)\"}...')
    exit(1)
" 2>&1

echo ""
echo "📝 Check API logs:"
echo "   docker compose logs api --tail 20 | grep -i gemini"
echo ""
echo "✅ Done!"


