#!/bin/bash
# Quick script to check API status

echo "=== API Status Check ==="
echo ""

echo "1. Testing API endpoint..."
if curl -s http://localhost:8000/health 2>&1 | grep -q "ok"; then
    echo "   ✅ API is responding!"
    curl -s http://localhost:8000/health
else
    echo "   ❌ API is NOT responding"
    echo ""
    echo "2. Checking if port 8000 is in use..."
    if lsof -i :8000 2>/dev/null | head -3; then
        echo "   Port 8000 is in use"
    else
        echo "   Port 8000 is NOT in use - API container might not be running"
    fi
    echo ""
    echo "3. Next steps:"
    echo "   Run: sudo docker compose ps"
    echo "   Run: sudo docker compose logs api"
    echo "   Run: sudo docker compose up -d"
fi

echo ""
echo "=== Done ==="

