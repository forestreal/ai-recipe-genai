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
