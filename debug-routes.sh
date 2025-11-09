#!/bin/bash
# Debug script to find why routes aren't loading

echo "=== Debugging Route Loading Issue ==="
echo ""

cd "$(dirname "$0")"

echo "1. Checking API container status..."
sudo docker compose ps api 2>/dev/null | grep api || echo "   Container might not be running"
echo ""

echo "2. Checking recent API logs for route import errors..."
echo "   (Look for 'ERROR: Failed to load routes' or import errors)"
echo ""
sudo docker compose logs api --tail 100 2>/dev/null | grep -A 10 -B 5 -i "error\|failed\|import\|traceback" | tail -50 || echo "   Could not check logs (need sudo)"
echo ""

echo "3. Testing if routes can be imported in container..."
sudo docker compose exec -T api python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from backend.routes import session, yap, diagnosis, flavor, analysis, recipes
    print('✅ All routes imported successfully')
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 || echo "   Could not test imports (need sudo)"
echo ""

echo "4. Checking available endpoints..."
ROUTES=$(curl -s http://localhost:8000/openapi.json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print('\n'.join(sorted(data.get('paths', {}).keys())))" 2>/dev/null)
if echo "$ROUTES" | grep -q "/api"; then
    echo "   ✅ Routes are loaded!"
    echo "$ROUTES" | grep "/api"
else
    echo "   ❌ Routes are NOT loaded"
    echo "   Only available: $ROUTES"
fi
echo ""

echo "=== Next Steps ==="
echo "If routes are not loading:"
echo "1. Check the full API logs: sudo docker compose logs api"
echo "2. Restart API: sudo docker compose restart api"
echo "3. Rebuild if needed: sudo docker compose up -d --build api"

