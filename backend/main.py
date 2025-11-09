import os
# formatted: minor whitespace/formatting update (non-functional)
from dotenv import load_dotenv
load_dotenv()
import uuid, json
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from backend.core.config import settings
from backend.redisx import r
#Few changes
DEFAULT_STATE = {
  "answers":{}, "flavor":{}, "yap_summary":[], "vibe":None,
  "evaluation_locked":False, "evaluation":None,
  "flavor_locked":False, "flavor_template":None,
  "analysis":None
}

app = FastAPI(title="AI Recipe GenAI")


@app.middleware("http")
async def permissive_cors(request: Request, call_next):
    """Catch OPTIONS preflight and echo the Origin header for all requests.
    This is a permissive dev-mode workaround so the frontend dev server
    (e.g., :5173) can call the API without browser CORS failures.
    It intentionally echoes the Origin header rather than using a wildcard
    so credentialed requests (with cookies) are accepted by browsers.
    """
    origin = request.headers.get("origin")
    # Handle preflight
    if request.method == "OPTIONS":
        resp = Response(status_code=200)
        if origin:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
        else:
            resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        # Mirror requested headers when present, else allow all
        acrh = request.headers.get("access-control-request-headers")
        resp.headers["Access-Control-Allow-Headers"] = acrh or "*"
        return resp

    # Non-preflight: call downstream and then attach CORS headers
    response = await call_next(request)
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    else:
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
    response.headers.setdefault("Access-Control-Allow-Credentials", "true")
    return response

@app.middleware("http")
async def attach_session(request: Request, call_next):
    sid = request.cookies.get("X-SESSION-ID") or uuid.uuid4().hex
    state = DEFAULT_STATE.copy()
    
    # Try to load session from Redis, but don't fail if Redis is unavailable
    try:
        if r is not None:
            raw = r.get(f"sess:{sid}")
            if raw:
                state = json.loads(raw)
    except Exception:
        # Redis not available or error - use default state
        pass
    
    request.state.session_id = sid
    request.state.session = state
    response: Response = await call_next(request)
    
    # Try to save session to Redis, but don't fail if Redis is unavailable
    try:
        if r is not None:
            r.setex(f"sess:{sid}", 60*60*24, json.dumps(request.state.session, default=lambda o: o.model_dump() if hasattr(o,"model_dump") else str(o)))
    except Exception:
        # Redis not available or error - continue without saving
        pass
    
    if "X-SESSION-ID" not in request.cookies:
        response.set_cookie("X-SESSION-ID", sid, httponly=True, samesite="Lax")
    return response

@app.get("/health")
def health(response: Response): 
    """Health check endpoint - doesn't depend on Redis or DB"""
    # Explicitly set CORS headers for health check
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {"ok": True}

# Import and include routers
try:
    from backend.routes import session, yap, diagnosis, flavor, analysis, recipes, debug
    app.include_router(session.router)
    app.include_router(yap.router)
    app.include_router(diagnosis.router)
    app.include_router(flavor.router)
    app.include_router(analysis.router)
    app.include_router(recipes.router)
    app.include_router(debug.router)
    print("✅ All routes loaded successfully")
except Exception as e:
    # Log error with full traceback
    import logging
    import traceback
    error_msg = f"Failed to load routes: {e}\n{traceback.format_exc()}"
    logging.error(error_msg)
    print(f"❌ ERROR: Failed to load routes")
    print(error_msg)
    # Don't crash - health endpoint should still work
    # But routes won't be available

# Serve the frontend static files from the backend so the app can be loaded from the
# same origin (no CORS required). This mounts the `frontend/` dir at root and will
# fall back to `index.html` for unknown paths (html=True).
try:
    from fastapi.staticfiles import StaticFiles
    # Mount static files under /static so that POST requests to the API
    # cannot be accidentally handled by StaticFiles (which may not support POST).
    app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")

    # Serve SPA index.html for browser GET requests at root and any path.
    # These are GET-only handlers so POSTs to these paths will not be swallowed
    # by the static file handler (which can produce 405/501 responses).
    @app.get("/", include_in_schema=False)
    async def spa_index():
        return FileResponse("frontend/index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_catchall(full_path: str):
        return FileResponse("frontend/index.html")

    print("✅ Frontend static files mounted at /static and root GET serves index.html")
except Exception as e:
    print(f"⚠️  Could not mount frontend static files: {e}")

# Verify Gemini API key on startup
@app.on_event("startup")
async def startup_event():
    """Verify Gemini API configuration on startup"""
    api_key = settings.GOOGLE_API_KEY
    if api_key:
        api_key = str(api_key).strip().strip('"').strip("'")
    
    if not api_key or api_key in ["your-api-key-here", "", "None", "null"]:
        print("⚠️  WARNING: GOOGLE_API_KEY not configured. AI features will use fallback mode.")
        print("   Set GOOGLE_API_KEY in .env file to enable Gemini API.")
    else:
        # Check if key looks valid (starts with AIzaSy)
        if api_key.startswith("AIzaSy"):
            print(f"✅ GOOGLE_API_KEY found: {api_key[:20]}...")
            print("   Gemini API will be used for AI features.")
        elif api_key.startswith("IzaSy"):
            print(f"⚠️  WARNING: API key appears incomplete (missing 'AI' prefix): {api_key[:20]}...")
            print("   Auto-fix will attempt to add the prefix.")
        else:
            print(f"⚠️  WARNING: API key format looks unusual: {api_key[:20]}...")
            print("   Verify your GOOGLE_API_KEY is correct.")
    # Print loaded CORS origins for verification
    try:
        print(f"✅ CORS origins loaded: {settings.CORS_ORIGINS}")
    except Exception:
        print("⚠️  Could not read CORS_ORIGINS from settings")
