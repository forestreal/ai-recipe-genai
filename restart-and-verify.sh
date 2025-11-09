#!/bin/bash
# Restart API and verify API key is loaded

echo "🔄 Restarting API to load API key from .env..."
echo ""

cd "$(dirname "$0")"

# Check API key in .env
API_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d'=' -f2-)

if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-api-key-here" ]; then
    echo "❌ API key not set in .env file!"
    echo "   Please edit .env and set GOOGLE_API_KEY=your-actual-key"
    exit 1
fi

echo "✅ API key found in .env: ${API_KEY:0:15}..."
echo ""

# Check if key looks valid (should start with AIzaSy)
if [[ ! "$API_KEY" =~ ^AIzaSy ]]; then
    echo "⚠️  WARNING: API key doesn't start with 'AIzaSy'"
    echo "   Google API keys usually start with 'AIzaSy...'"
    echo "   Make sure you copied the entire key!"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Restarting API container..."
sudo docker compose restart api

echo ""
echo "⏳ Waiting for API to restart..."
sleep 10

echo ""
echo "✅ API restarted!"
echo ""
echo "Now try using the AI features in your browser."
echo "If you still get errors, check:"
echo "  sudo docker compose logs api --tail 30"

