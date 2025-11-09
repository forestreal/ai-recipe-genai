from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session as OrmSession
from backend.schemas.analysis import CulinaryAnalysis
from backend.services.llm import call_json_strict
from fastapi.responses import JSONResponse
from backend.models import Analysis as AnalysisRow
from backend.db import get_db
from backend.auth import get_current_user
from backend.models import User
import json

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/compile", response_model=CulinaryAnalysis)
def compile_analysis(req: Request, current_user: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    s = req.state.session
    if not (s.get("evaluation_locked") and s.get("flavor_locked")):
        raise HTTPException(status_code=400, detail="Lock evaluation and flavor first")

    prompt = (
        "Return JSON ONLY with keys: version, core_attributes, leaning_cuisines, "
        "cooking_styles, ingredient_bias, taste_notes, summary (≤60 words, PG, no numbers).\n\n"
        f"EVALUATION: {json.dumps(s['evaluation'].model_dump(), ensure_ascii=False)}\n"
        f"FLAVOR: {json.dumps(s['flavor_template'].model_dump(), ensure_ascii=False)}\n"
    )
    # call_json_strict now returns dict with possible 'error' key instead of raising
    data = call_json_strict(prompt)
    if isinstance(data, dict) and data.get("error"):
        return JSONResponse(status_code=503, content={"error": data.get("error")})
    s["analysis"] = data
    db.add(AnalysisRow(user_id=current_user.id, content=data))
    db.commit()
    return data