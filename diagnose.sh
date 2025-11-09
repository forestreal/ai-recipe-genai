#!/bin/bash
# Diagnostic script to check application status

echo "=== AI Recipe GenAI Diagnostic ==="
echo ""

echo "=== Container Status ==="
sudo docker compose ps 2>/dev/null || docker compose ps
echo ""

echo "=== API Logs (last 30 lines) ==="
sudo docker compose logs api --tail 30 2>/dev/null || docker compose logs api --tail 30
echo ""

echo "=== Redis Test ==="
if sudo docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis is NOT responding"
fi
echo ""

echo "=== Database Test ==="
if sudo docker compose exec -T db psql -U app -d recipe -c "SELECT 1;" 2>/dev/null | grep -q "1"; then
    echo "✅ Database is responding"
else
    echo "❌ Database is NOT responding"
fi
echo ""

echo "=== Health Check ==="
if curl -s http://localhost:8000/health 2>/dev/null | grep -q "ok"; then
    echo "✅ API health check passed"
    curl -s http://localhost:8000/health
else
    echo "❌ API health check failed"
    echo "   API is not responding on http://localhost:8000/health"
fi
echo ""

echo "=== Port Status ==="
echo "Port 8000:"
sudo lsof -i :8000 2>/dev/null || echo "  (check requires sudo)"
echo ""

echo "=== Environment Check ==="
if [ -f .env ]; then
    echo "✅ .env file exists"
    if grep -q "your-api-key-here" .env; then
        echo "⚠️  WARNING: GOOGLE_API_KEY is still set to placeholder"
    fi
else
    echo "❌ .env file missing"
fi
echo ""

echo "=== Recommendations ==="
echo "If API is not working:"
echo "1. Check logs: sudo docker compose logs api"
echo "2. Restart services: sudo docker compose restart"
echo "3. Rebuild: sudo docker compose up -d --build"
echo "4. See TROUBLESHOOTING.md for more help"

