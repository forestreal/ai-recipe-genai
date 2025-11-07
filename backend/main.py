import uuid, json
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.redisx import r

DEFAULT_STATE = {
  "answers":{}, "flavor":{}, "yap_summary":[], "vibe":None,
  "evaluation_locked":False, "evaluation":None,
  "flavor_locked":False, "flavor_template":None,
  "analysis":None
}

app = FastAPI(title="AI Recipe GenAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def attach_session(request: Request, call_next):
    sid = request.cookies.get("X-SESSION-ID") or uuid.uuid4().hex
    raw = r.get(f"sess:{sid}")
    state = json.loads(raw) if raw else DEFAULT_STATE.copy()
    request.state.session_id = sid
    request.state.session = state
    response: Response = await call_next(request)
    r.setex(f"sess:{sid}", 60*60*24, json.dumps(request.state.session, default=lambda o: o.model_dump() if hasattr(o,"model_dump") else str(o)))
    if "X-SESSION-ID" not in request.cookies:
        response.set_cookie("X-SESSION-ID", sid, httponly=True, samesite="Lax")
    return response

@app.get("/health")
def health(): return {"ok": True}

from backend.routes import session, yap, diagnosis, flavor, analysis, recipes
app.include_router(session.router)
app.include_router(yap.router)
app.include_router(diagnosis.router)
app.include_router(flavor.router)
app.include_router(analysis.router)
app.include_router(recipes.router)