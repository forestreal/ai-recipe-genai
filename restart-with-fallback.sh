#!/bin/bash
# Restart API with fallback mode enabled

cd "$(dirname "$0")"

echo "🔄 Restarting API with fallback mode..."
echo ""
echo "✅ Fixed API key in .env (added 'AI' prefix)"
echo "✅ Added fallback mode - app will work even with invalid API key"
echo ""

# Restart the API container
echo "Restarting API container..."
docker compose restart api

echo ""
echo "⏳ Waiting 10 seconds for API to start..."
sleep 10

echo ""
echo "✅ Done! The API should now work with fallback mode."
echo ""
echo "📝 What changed:"
echo "   - Fixed API key format in .env"
echo "   - Added fallback mode (returns demo responses if API key fails)"
echo "   - Frontend will now work even with invalid/missing API key"
echo ""
echo "🧪 Test it:"
echo "   curl http://localhost:8000/health"
echo ""
echo "💡 To get real AI responses, configure a valid Google Gemini API key:"
echo "   https://makersuite.google.com/app/apikey"

