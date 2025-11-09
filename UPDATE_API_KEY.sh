#!/bin/bash
# Helper script to update API key

echo "🔑 Google Gemini API Key Setup"
echo ""

cd "$(dirname "$0")"

# Check current value
CURRENT_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d'=' -f2)

if [ "$CURRENT_KEY" = "your-api-key-here" ] || [ -z "$CURRENT_KEY" ]; then
    echo "❌ API key is not set (still using placeholder)"
    echo ""
    echo "📋 Steps to fix:"
    echo ""
    echo "1. Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "2. Edit the .env file:"
    echo "   nano .env"
    echo ""
    echo "3. Find this line:"
    echo "   GOOGLE_API_KEY=your-api-key-here"
    echo ""
    echo "4. Replace 'your-api-key-here' with your actual API key"
    echo "   (It should look like: GOOGLE_API_KEY=AIzaSy...)"
    echo ""
    echo "5. Save and exit (Ctrl+X, Y, Enter)"
    echo ""
    echo "6. Restart the API:"
    echo "   sudo docker compose restart api"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
    
    # Check again
    NEW_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d'=' -f2)
    if [ "$NEW_KEY" != "your-api-key-here" ] && [ -n "$NEW_KEY" ]; then
        echo ""
        echo "✅ API key updated!"
        echo ""
        echo "Restarting API..."
        sudo docker compose restart api
        echo ""
        echo "⏳ Waiting for API to restart..."
        sleep 8
        echo ""
        echo "✅ Done! Try using the AI features now."
    else
        echo ""
        echo "⚠️  API key still not updated. Make sure you:"
        echo "   - Saved the .env file"
        echo "   - Replaced 'your-api-key-here' with your actual key"
        echo "   - Didn't add quotes around the key"
    fi
else
    echo "✅ API key is set: ${CURRENT_KEY:0:20}..."
    echo ""
    echo "If you're still getting errors, try:"
    echo "  sudo docker compose restart api"
fi

