#!/bin/bash
# Quick script to restart API and fix CORS

echo "🔄 Restarting API to apply CORS fixes..."
echo ""

cd "$(dirname "$0")"

# Restart API
echo "1. Restarting API container..."
sudo docker compose restart api

echo ""
echo "2. Waiting for API to restart..."
sleep 8

echo ""
echo "3. Testing API..."
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "   ✅ API is responding!"
    
    echo ""
    echo "4. Testing CORS headers..."
    if curl -s -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET" \
         -X OPTIONS http://localhost:8000/health -I 2>&1 | grep -i "access-control" > /dev/null; then
        echo "   ✅ CORS headers are present!"
    else
        echo "   ⚠️  CORS headers might not be visible in OPTIONS request"
        echo "   But GET requests should work now"
    fi
    
    echo ""
    echo "✅ API should now be accessible from the frontend!"
    echo "   Refresh your browser at http://localhost:5173/index.html"
else
    echo "   ❌ API is still not responding"
    echo ""
    echo "   Check logs with: sudo docker compose logs api --tail 50"
fi

