# Restart Instructions After Fixes

## The Problem
The API was crashing with "Connection reset by peer" because:
1. Redis connection failures were crashing the middleware
2. No error handling for when Redis is unavailable

## The Fixes
I've made the following changes:
1. ✅ Added error handling in middleware for Redis failures
2. ✅ Made Redis connection more resilient with better error handling
3. ✅ Made rate limiting fail gracefully when Redis is unavailable
4. ✅ Added error handling for route imports

## How to Restart

### Step 1: Rebuild the Container
Since we changed the code, we need to rebuild:

```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai

# Stop everything
sudo docker compose down

# Rebuild with the new code
sudo docker compose up -d --build
```

### Step 2: Wait for Services
The health checks ensure services start in the right order, but give them time:

```bash
# Wait 15-20 seconds for everything to start
sleep 15
```

### Step 3: Initialize Database
```bash
sudo docker compose exec api python -m backend.init_db
```

### Step 4: Test Health Endpoint
```bash
curl http://localhost:8000/health
```

You should see: `{"ok":true}`

### Step 5: Check Logs (if still having issues)
```bash
# Check API logs
sudo docker compose logs api --tail 50

# Check all logs
sudo docker compose logs --tail 50
```

## What Changed

### backend/main.py
- Middleware now handles Redis errors gracefully
- Health endpoint works even if Redis/DB are down
- Route imports have error handling

### backend/redisx.py
- Better connection retry logic
- Proper error handling
- Graceful degradation when Redis is unavailable

### docker-compose.yaml
- Added health checks for db and redis
- API waits for dependencies to be healthy before starting
- Added restart policies

## Expected Behavior

✅ **API should start even if Redis is temporarily unavailable**
✅ **Health endpoint should work immediately**
✅ **Session storage will work once Redis is available**
✅ **No more crashes from Redis connection issues**

## If Still Not Working

Run the diagnostic script:
```bash
./diagnose.sh
```

Or check logs manually:
```bash
sudo docker compose logs api --tail 100
```

Share the error messages and we can fix them!

