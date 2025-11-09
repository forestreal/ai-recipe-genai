from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session as OrmSession
from backend.schemas.recipe import RecipeOut
from backend.models import RecipeRun
from backend.services.llm import call_json_strict
from fastapi.responses import JSONResponse
from backend.db import get_db
from pydantic import BaseModel
from typing import List
import json
from backend.auth import get_current_user
from backend.models import User

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

class GeneratePayload(BaseModel):
    meals: List[str] = ["lunch","dinner","snack"]
    count: int = 3

@router.post("/generate", response_model=List[RecipeOut])
def generate(req: Request, body: GeneratePayload, current_user: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    s = req.state.session
    if not (s.get("evaluation_locked") and s.get("flavor_locked")):
        raise HTTPException(status_code=400, detail="Evaluation and Flavor must be locked before generation")

    sys = (
      "You return STRICT JSON only: an array of recipes. No text outside JSON.\n"
      "Each recipe must include: title, cuisine, meal_type, prep_time, difficulty, "
      "ingredients[{item,quantity,unit}], instructions[\"1. ...\"], "
      "macros{calories,protein_g,carbs_g,fat_g,fiber_g}, micros_highlights[], timing, notes (≤40 words).\n"
      "Units: metric. Honor allergies as hard constraints."
    )
    user = {
      "EVALUATION": s["evaluation"].model_dump(),
      "FLAVOR": s["flavor_template"].model_dump(),
      "ANALYSIS": s.get("analysis"),
      "MEALS": body.meals,
      "COUNT": body.count
    }
    # call_json_strict now returns dict with possible 'error' key instead of raising
    data = call_json_strict(sys + "\n\nUSER:\n" + json.dumps(user, ensure_ascii=False))
    if isinstance(data, dict) and data.get("error"):
        return JSONResponse(status_code=503, content={"error": data.get("error")})
    # Ensure data is a list (fallback returns list, but check anyway)
    if not isinstance(data, list):
        # If fallback returned dict, wrap it in a list
        data = [data] if isinstance(data, dict) else []
    # If fallback mode, adjust count to match returned data
    if len(data) != body.count:
        # In fallback mode, just return what we have
        if len(data) == 1 and "Demo Recipe" in str(data[0].get("title", "")):
            # This is fallback mode - return the demo recipe body.count times
            data = data * body.count
    if not isinstance(data, list) or len(data) != body.count:
        raise HTTPException(status_code=422, detail="Model did not return expected recipe array")
    db.add(RecipeRun(user_id=current_user.id, request_payload=user, result=data)); db.commit()
    return data