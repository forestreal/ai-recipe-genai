# Starting the Application

## Option 1: Using Docker (Recommended)

### Step 1: Start Docker Service
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Optional: enable on boot
```

### Step 2: Start the Application
```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai

# Start all services (database, redis, API)
docker compose up -d

# Initialize database tables
docker compose exec api python backend/init_db.py

# Check if API is running
curl http://localhost:8000/health
```

### Step 3: Access the Application
- **API**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Frontend**: 
  ```bash
  cd frontend
  python3 -m http.server 5173
  ```
  Then open: http://localhost:5173/diagnosis.html

### Useful Commands
```bash
# View logs
docker compose logs -f api

# Stop services
docker compose down

# Restart services
docker compose restart
```

---

## Option 2: Run Locally (Without Docker)

### Prerequisites
- PostgreSQL running locally (or update DATABASE_URL)
- Redis running locally (or update REDIS_URL)
- Python 3.11+

### Step 1: Set up Virtual Environment
```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Update .env for Local Services
Update `.env` file:
```bash
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/recipe
REDIS_URL=redis://localhost:6379/0
GOOGLE_API_KEY=your-api-key-here
JWT_SECRET=change-me-to-a-secure-random-string
CORS_ORIGINS=http://localhost:5173
```

### Step 3: Start PostgreSQL and Redis
```bash
# PostgreSQL (if not running)
sudo systemctl start postgresql

# Redis (if not running)
sudo systemctl start redis
```

### Step 4: Initialize Database
```bash
# Make sure PostgreSQL database exists
createdb recipe  # or use psql to create it

# Initialize tables
python backend/init_db.py
```

### Step 5: Start the API
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Start Frontend (in another terminal)
```bash
cd frontend
python3 -m http.server 5173
```

---

## Important Notes

1. **Google API Key**: You MUST set `GOOGLE_API_KEY` in `.env` for the LLM features to work.
   - Get your key from: https://makersuite.google.com/app/apikey

2. **Database**: The app expects a PostgreSQL database named `recipe` with user `app` and password `app`.

3. **Redis**: Used for session management. Make sure it's running.

4. **Fixed Issues**: 
   - ✅ Fixed syntax errors in `analysis.py`, `flavor.py`, `recipes.py`
   - ✅ Fixed `init_db.py` import paths

---

## Troubleshooting

### Docker Issues
- If Docker daemon is not running: `sudo systemctl start docker`
- If port 8000 is already in use: Change port in `docker-compose.yaml`

### Database Issues
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Check connection: `psql -h localhost -U app -d recipe`

### Redis Issues
- Check if Redis is running: `sudo systemctl status redis`
- Test connection: `redis-cli ping` (should return `PONG`)

### API Key Issues
- Make sure `GOOGLE_API_KEY` is set in `.env`
- The app will start but LLM features won't work without it

