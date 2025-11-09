#!/bin/bash
# Restart API with new Gemini API key

cd "$(dirname "$0")"

echo "🔄 Restarting API with new Gemini API key..."
echo ""

# Verify API key is set
API_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d'=' -f2)
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-api-key-here" ]; then
    echo "❌ Error: GOOGLE_API_KEY not set in .env"
    exit 1
fi

echo "✅ API key found: ${API_KEY:0:20}..."
echo ""

# Restart the API container
echo "Restarting API container..."
sudo docker compose restart api

echo ""
echo "⏳ Waiting 15 seconds for API to start..."
sleep 15

echo ""
echo "✅ API restarted!"
echo ""
echo "🧪 Testing API..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is responding"
else
    echo "⚠️  API might still be starting..."
fi

echo ""
echo "📝 Check logs:"
echo "   sudo docker compose logs api --tail 30 | grep -i 'gemini\|api\|key'"
echo ""
echo "💡 The Yap feature should now use the real Gemini API!"

