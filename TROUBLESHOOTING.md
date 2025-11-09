# Troubleshooting Guide

## API Health Check Failing

If the API health check fails, here are the most common causes and solutions:

### Step 1: Check Container Status

Run this command to see if containers are running:
```bash
sudo docker compose ps
```

You should see all three services (api, db, redis) with status "Up". If any are "Exited" or "Restarting", that's the problem.

### Step 2: Check API Logs

The most important step - check what error the API is showing:
```bash
sudo docker compose logs api --tail 100
```

Common errors you might see:

#### Error: "Connection refused" to Redis
**Problem**: Redis isn't ready when API starts
**Solution**: 
```bash
# Restart the API container (it will retry Redis connection)
sudo docker compose restart api

# Or restart everything
sudo docker compose restart
```

#### Error: "ModuleNotFoundError" or Import errors
**Problem**: Missing dependencies or import issues
**Solution**:
```bash
# Rebuild the container
sudo docker compose up -d --build api
```

#### Error: "Connection refused" to Database
**Problem**: Database isn't ready
**Solution**:
```bash
# Wait a bit longer, then restart API
sleep 10
sudo docker compose restart api
```

### Step 3: Check Redis Connection

Test if Redis is accessible:
```bash
sudo docker compose exec redis redis-cli ping
```

Should return: `PONG`

If it fails, restart Redis:
```bash
sudo docker compose restart redis
```

### Step 4: Check Database Connection

Test if database is accessible:
```bash
sudo docker compose exec db psql -U app -d recipe -c "SELECT 1;"
```

Should return: `1`

If it fails, check database logs:
```bash
sudo docker compose logs db --tail 50
```

### Step 5: Common Fixes

#### Fix 1: Restart All Services
```bash
sudo docker compose down
sudo docker compose up -d
sleep 10
sudo docker compose exec api python -m backend.init_db
curl http://localhost:8000/health
```

#### Fix 2: Rebuild Everything
```bash
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
sleep 10
sudo docker compose exec api python -m backend.init_db
```

#### Fix 3: Check Port Conflicts
```bash
# Check if port 8000 is in use
sudo lsof -i :8000

# If something is using it, stop it or change port in docker-compose.yaml
```

#### Fix 4: Increase Startup Wait Time

The startup script waits 5 seconds, but sometimes services need more time. Try:
```bash
sudo docker compose up -d
sleep 15  # Wait longer
sudo docker compose exec api python -m backend.init_db
curl http://localhost:8000/health
```

### Step 6: View All Logs

See what's happening with all services:
```bash
# All services
sudo docker compose logs --tail 100

# Follow logs in real-time
sudo docker compose logs -f

# Specific service
sudo docker compose logs -f api
```

### Step 7: Check Environment Variables

Make sure .env file is correct:
```bash
cat .env
```

Key things to check:
- `DATABASE_URL` should point to `db:5432` (not `localhost`)
- `REDIS_URL` should point to `redis:6379` (not `localhost`)
- `GOOGLE_API_KEY` can be placeholder for now

### Step 8: Manual Container Inspection

If nothing works, inspect the container:
```bash
# Get into the API container
sudo docker compose exec api bash

# Inside container, test imports
python -c "from backend.main import app; print('OK')"

# Test Redis connection
python -c "from backend.redisx import r; print(r.ping())"

# Test database connection
python -c "from backend.db import engine; print(engine.connect())"
```

## Quick Diagnostic Script

Run this to get a full diagnostic:
```bash
echo "=== Container Status ==="
sudo docker compose ps

echo ""
echo "=== API Logs (last 20 lines) ==="
sudo docker compose logs api --tail 20

echo ""
echo "=== Redis Test ==="
sudo docker compose exec -T redis redis-cli ping || echo "Redis failed"

echo ""
echo "=== Database Test ==="
sudo docker compose exec -T db psql -U app -d recipe -c "SELECT 1;" || echo "Database failed"

echo ""
echo "=== Health Check ==="
curl -s http://localhost:8000/health || echo "API not responding"
```

## Still Not Working?

If none of the above works, try:

1. **Complete reset**:
   ```bash
   sudo docker compose down -v  # Removes volumes too
   sudo docker compose up -d --build
   sleep 15
   sudo docker compose exec api python -m backend.init_db
   ```

2. **Check Docker resources**:
   ```bash
   sudo docker system df
   sudo docker system prune  # Clean up if needed
   ```

3. **Check system resources**:
   ```bash
   free -h
   df -h
   ```

4. **Share the logs**: Copy the output of:
   ```bash
   sudo docker compose logs api --tail 50
   ```

