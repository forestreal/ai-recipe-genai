# AI Recipe GenAI

- **v2/** → Current active version (Docker + FastAPI + Redis + Gemini).
- **v1/** → Legacy submission snapshot.

## Quick start (v2)
1) Copy `.env.example` → `.env` and fill values.
2) docker compose up -d
3) docker compose exec api python backend/init_db.py
4) API: http://localhost:8000/health
5) Frontend: from frontend/ → python -m http.server 5173 → http://localhost:5173/diagnosis.html

ai-recipe-gen



what this is
	•	chat + qna that ends in a custom recipe
	•	you answer some flavor / pantry questions, can “yap” to the model if you want
	•	backend collects everything, calls gemini, returns a single clean recipe json + text
	•	simple front end to run it, nothing fancy

stack
	•	frontend: vanilla js + html, small scripts, no framework
	•	backend: fastapi (python)
	•	llm: gemini (models 1.5/2.5, configurable)
	•	storage: basic file/db stub for session + answers

demo: 
https://github.com/user-attachments/assets/321e722a-feb0-4eb6-b158-bfaf588ea2ab




## Local Setup

Follow the steps below to run the project locally.

### 1. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create your `.env` file
Copy the example environment file:
```bash
cp .env.example .env
```

Fill in the required values inside `.env`:

- GOOGLE_API_KEY or GEMINI_API_KEY – add your own API key  
- DATABASE_URL – use default or your own  
- REDIS_URL – optional  
- JWT_SECRET – change to a long random value  
- CORS_ORIGINS – leave default unless you need something else  

(All required variables are listed in `.env.example`.)

### 3. Run the backend API
```bash
uvicorn backend.core.main:app --reload
```

Backend runs at:
```
http://localhost:8000
```

### 4. Run the frontend
Open:
```
frontend/index.html
```
directly in your browser.
