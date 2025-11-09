#!/bin/bash
# Script to fix API connection issues

echo "🔧 Fixing API Connection Issues..."
echo ""

cd "$(dirname "$0")"

# Check if API is responding
echo "1. Checking API health..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ API is responding"
else
    echo "   ❌ API is not responding"
    echo ""
    echo "   Starting Docker services..."
    sudo docker compose up -d
    echo "   Waiting for services to start..."
    sleep 10
fi

# Check CORS configuration
echo ""
echo "2. Checking CORS configuration..."
if grep -q "http://localhost:5173" .env; then
    echo "   ✅ CORS is configured for localhost:5173"
else
    echo "   ⚠️  CORS might not be configured correctly"
    echo "   Make sure .env has: CORS_ORIGINS=http://localhost:5173"
fi

# Restart API to ensure CORS is active
echo ""
echo "3. Restarting API to apply CORS settings..."
sudo docker compose restart api

echo ""
echo "4. Waiting for API to restart..."
sleep 5

# Test CORS
echo ""
echo "5. Testing CORS headers..."
curl -s -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/health -v 2>&1 | grep -i "access-control" || echo "   ⚠️  CORS headers not visible in OPTIONS"

# Final health check
echo ""
echo "6. Final API health check..."
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "   ✅ API is ready!"
    echo ""
    echo "🎉 API should now be accessible from the frontend!"
    echo "   Try refreshing your browser at http://localhost:5173/index.html"
else
    echo "   ❌ API is still not responding"
    echo "   Check logs with: sudo docker compose logs api"
fi

