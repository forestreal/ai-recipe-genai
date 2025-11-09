# Quick Start Guide

## Step 1: Start Docker Service

You need to start Docker first (requires sudo):

```bash
sudo systemctl start docker
```

**Optional**: To run Docker without sudo in the future:
```bash
sudo usermod -aG docker $USER
# Then log out and log back in
```

## Step 2: Update API Key (Important!)

Edit `.env` and replace `your-api-key-here` with your actual Google Gemini API key:

```bash
nano .env
# or
vim .env
```

Get your API key from: https://makersuite.google.com/app/apikey

## Step 3: Start the Application

### Option A: Use the startup script (easiest)
```bash
./start.sh
```

### Option B: Manual steps
```bash
# Start all services
docker compose up -d

# Initialize database
docker compose exec api python backend/init_db.py

# Check if running
curl http://localhost:8000/health
```

## Step 4: Access the Application

- **API Health**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: 
  ```bash
  cd frontend
  python3 -m http.server 5173
  ```
  Then open: http://localhost:5173/diagnosis.html

## Troubleshooting

### Docker not starting?
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Enable Docker on boot (optional)
sudo systemctl enable docker
```

### View logs
```bash
# All services
docker compose logs -f

# Just the API
docker compose logs -f api

# Database
docker compose logs -f db
```

### Stop services
```bash
docker compose down
```

### Restart services
```bash
docker compose restart
```

### Rebuild after code changes
```bash
docker compose up -d --build
```

### Database issues?
```bash
# Reinitialize database
docker compose exec api python backend/init_db.py

# Access PostgreSQL directly
docker compose exec db psql -U app -d recipe
```

## What's Running?

- **API**: FastAPI backend on port 8000
- **PostgreSQL**: Database on port 5432
- **Redis**: Session storage on port 6379

All services are accessible from localhost.

