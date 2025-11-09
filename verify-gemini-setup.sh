#!/bin/bash
# Verify Gemini API setup

cd "$(dirname "$0")"

echo "🔍 Verifying Gemini API Setup..."
echo ""

# Check .env file
echo "1. Checking .env file..."
if [ -f .env ]; then
    API_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d'=' -f2)
    if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-api-key-here" ]; then
        echo "   ❌ GOOGLE_API_KEY not set or is placeholder"
    else
        if [[ "$API_KEY" == AIzaSy* ]]; then
            echo "   ✅ API key found: ${API_KEY:0:20}..."
        else
            echo "   ⚠️  API key format unusual: ${API_KEY:0:20}..."
        fi
    fi
else
    echo "   ❌ .env file not found"
fi

echo ""
echo "2. Checking API container status..."
if sudo docker compose ps api | grep -q "Up"; then
    echo "   ✅ API container is running"
else
    echo "   ❌ API container is not running"
    echo "   Run: sudo docker compose up -d api"
fi

echo ""
echo "3. Checking API health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ API is responding"
else
    echo "   ❌ API is not responding"
fi

echo ""
echo "4. Checking API logs for Gemini initialization..."
echo "   (Last 20 lines)"
sudo docker compose logs api --tail 20 | grep -E "(Gemini|API|key|initialized|✅|⚠️)" | tail -5 || echo "   No relevant logs found"

echo ""
echo "5. Testing API key in container..."
sudo docker compose exec -T api python -c "
from backend.core.config import settings
import sys
if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY not in ['', 'your-api-key-here', 'None']:
    print(f'   ✅ API key loaded: {settings.GOOGLE_API_KEY[:20]}...')
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-pro')
        print('   ✅ Gemini API can be initialized')
    except Exception as e:
        print(f'   ⚠️  Gemini API init error: {str(e)[:100]}')
else:
    print('   ❌ API key not loaded in container')
    sys.exit(1)
" 2>&1 | sed 's/^/   /'

echo ""
echo "✅ Verification complete!"
echo ""
echo "📝 Next steps:"
echo "   - If API key is missing, update .env file"
echo "   - Restart API: sudo docker compose restart api"
echo "   - Test Yap feature in frontend"

