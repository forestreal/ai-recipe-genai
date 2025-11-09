#!/bin/bash
# Script to help fix API key issue

echo "🔑 Fixing Google Gemini API Key Issue"
echo ""

cd "$(dirname "$0")"

# Check current .env
CURRENT=$(grep "^GOOGLE_API_KEY=" .env 2>/dev/null | cut -d'=' -f2-)

if [ -z "$CURRENT" ] || [ "$CURRENT" = "your-api-key-here" ]; then
    echo "❌ API key is still set to placeholder: 'your-api-key-here'"
    echo ""
    echo "📝 You need to:"
    echo "   1. Get your API key from: https://makersuite.google.com/app/apikey"
    echo "   2. Edit .env file: nano .env"
    echo "   3. Replace 'your-api-key-here' with your actual key"
    echo "   4. Save and restart API"
    echo ""
    echo "Would you like to edit the .env file now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        nano .env
        echo ""
        echo "✅ File edited. Now restarting API..."
        sudo docker compose restart api
        sleep 8
        echo ""
        echo "✅ API restarted. Try using the AI features now!"
    else
        echo ""
        echo "Manual steps:"
        echo "  1. nano .env"
        echo "  2. Change GOOGLE_API_KEY=your-api-key-here to GOOGLE_API_KEY=your-actual-key"
        echo "  3. sudo docker compose restart api"
    fi
else
    echo "✅ API key is set in .env file"
    echo "   Key: ${CURRENT:0:20}..."
    echo ""
    echo "But you're still getting errors. This might mean:"
    echo "  1. API container needs restart"
    echo "  2. .env file isn't being read by container"
    echo ""
    echo "Restarting API to reload .env..."
    sudo docker compose restart api
    sleep 8
    echo ""
    echo "✅ API restarted. Try again now!"
fi

