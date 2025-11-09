# Step-by-Step Startup Guide

## Current Status ✅
- ✅ All syntax errors fixed
- ✅ Dockerfile created
- ✅ docker-compose.yaml ready
- ✅ .env file created
- ✅ init_db.py fixed
- ✅ start.sh script ready

## Step 1: Fix Docker Permissions (Choose One Option)

### Option A: Use sudo for Docker commands (Quick)
You'll need to use `sudo` before docker commands. This is fine for now.

### Option B: Add yourself to docker group (Recommended for long-term)
Run this command in your terminal:
```bash
sudo usermod -aG docker $USER
```
Then **log out and log back in** (or restart your terminal session) for it to take effect.

**For now, let's proceed with Option A (using sudo).**

---

## Step 2: Check Docker Status

Run this command:
```bash
sudo docker ps
```

You should see an empty list (or running containers). If you see an error, let me know.

---

## Step 3: Update API Key (IMPORTANT!)

Before starting, you need to set your Google Gemini API key.

1. Get your API key from: https://makersuite.google.com/app/apikey
2. Edit the `.env` file:
   ```bash
   nano .env
   # or
   vim .env
   ```
3. Find this line:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```
4. Replace `your-api-key-here` with your actual API key
5. Save and exit (Ctrl+X, then Y, then Enter for nano)

**Note**: The app will start without a valid API key, but LLM features won't work.

---

## Step 4: Start the Application

### Option A: Use the startup script (Easiest)

Since we need sudo, let's modify the approach. Run these commands one by one:

```bash
# Navigate to project directory
cd /home/straycat/Coding/meenaapp/ai-recipe-genai

# Start all services
sudo docker compose up -d

# Wait a few seconds for services to start
sleep 5

# Initialize database
sudo docker compose exec api python backend/init_db.py

# Check if API is running
curl http://localhost:8000/health
```

### Option B: Manual step-by-step

```bash
# 1. Start database
sudo docker compose up -d db

# 2. Start Redis
sudo docker compose up -d redis

# 3. Wait for database to be ready
sleep 3

# 4. Start API
sudo docker compose up -d api

# 5. Wait for API to start
sleep 5

# 6. Initialize database tables
sudo docker compose exec api python backend/init_db.py

# 7. Check health
curl http://localhost:8000/health
```

---

## Step 5: Verify Everything is Running

Run these commands to check:

```bash
# Check all containers are running
sudo docker compose ps

# Check API logs
sudo docker compose logs api

# Test API endpoint
curl http://localhost:8000/health
```

You should see: `{"ok":true}`

---

## Step 6: Access the Application

### API Endpoints:
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

### Frontend:
Open a new terminal and run:
```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai/frontend
python3 -m http.server 5173
```

Then open in your browser: http://localhost:5173/diagnosis.html

---

## Troubleshooting

### If containers fail to start:
```bash
# View logs
sudo docker compose logs

# View specific service logs
sudo docker compose logs api
sudo docker compose logs db
sudo docker compose logs redis
```

### If database initialization fails:
```bash
# Check if database is ready
sudo docker compose exec db psql -U app -d recipe -c "SELECT 1;"

# Re-run initialization
sudo docker compose exec api python backend/init_db.py
```

### If port 8000 is already in use:
```bash
# Find what's using the port
sudo lsof -i :8000

# Or change the port in docker-compose.yaml
```

### To stop everything:
```bash
sudo docker compose down
```

### To restart:
```bash
sudo docker compose restart
```

### To rebuild after code changes:
```bash
sudo docker compose up -d --build
```

---

## Quick Reference Commands

```bash
# Start everything
sudo docker compose up -d

# Stop everything
sudo docker compose down

# View logs
sudo docker compose logs -f

# Restart a service
sudo docker compose restart api

# Rebuild and restart
sudo docker compose up -d --build

# Access database
sudo docker compose exec db psql -U app -d recipe

# Access API container shell
sudo docker compose exec api bash
```

---

## Next Steps After Startup

1. ✅ Verify API is running: http://localhost:8000/health
2. ✅ Check API docs: http://localhost:8000/docs
3. ✅ Start frontend server
4. ✅ Test the application flow

Let me know which step you're on and I'll help you through it!

