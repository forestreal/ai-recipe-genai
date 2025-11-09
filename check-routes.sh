#!/bin/bash
# Check if routes are loaded

echo "=== Checking API Routes ==="
echo ""

echo "1. Testing health endpoint..."
curl -s http://localhost:8000/health && echo "" || echo "❌ Health endpoint failed"
echo ""

echo "2. Testing if routes are loaded..."
ROUTES=$(curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; data=json.load(sys.stdin); print('\n'.join(sorted(data.get('paths', {}).keys())))" 2>/dev/null)

if echo "$ROUTES" | grep -q "/api"; then
    echo "✅ Routes are loaded!"
    echo ""
    echo "Available API endpoints:"
    echo "$ROUTES" | grep "/api" | sed 's/^/  /'
else
    echo "❌ Routes are NOT loaded!"
    echo ""
    echo "Only these endpoints are available:"
    echo "$ROUTES" | sed 's/^/  /'
    echo ""
    echo "This means the routes failed to import."
    echo "Check API logs with: sudo docker compose logs api"
fi

echo ""
echo "=== Done ==="

