# AI Recipe GenAI

- **v2/** → Current active version (Docker + FastAPI + Redis + Gemini).
- **v1/** → Legacy submission snapshot.

## Quick start (v2)
1) Copy `.env.example` → `.env` and fill values.
2) docker compose up -d
3) docker compose exec api python backend/init_db.py
4) API: http://localhost:8000/health
5) Frontend: from frontend/ → python -m http.server 5173 → http://localhost:5173/diagnosis.html
