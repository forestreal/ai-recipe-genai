from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as OrmSession
from backend.db import get_db
from backend.services.evaluation import build_snapshot
from backend.schemas.evaluation import EvaluationRequest, EvaluationResponse
from backend.models import Evaluation

router = APIRouter(prefix="/api/diagnosis", tags=["diagnosis"])

class AnswerIn(BaseModel):
    question_id: str
    value: str | int | float | bool | list | None

@router.post("/answer")
def answer(req: Request, body: AnswerIn):
    s = req.state.session
    s["answers"][body.question_id] = body.value
    return {"ok": True}

@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(req: Request, body: EvaluationRequest, db: OrmSession = Depends(get_db)):
    s = req.state.session
    if s.get("evaluation_locked") and not body.force:
        snap = s["evaluation"]
    else:
        snap = build_snapshot(s)
        s["evaluation"] = snap
        s["evaluation_locked"] = True
        if not s.get("vibe"):
            s["vibe"] = "Dialed and focused—let’s engineer meals that fit your day and taste."
            snap.persona.vibe_line = s["vibe"]
    public = {
        "somatotype": snap.somatotype,
        "fitness_goal": snap.fitness_goal,
        "constraints": {"allergies": snap.constraints.get("allergies", []), "dislikes": snap.constraints.get("dislikes", [])},
        "vibe": snap.persona.vibe_line or ""
    }
    # Persist (replace 1 with real user ID if you wire auth)
    db.add(Evaluation(user_id=1, snapshot=snap.model_dump(), locked=True))
    db.commit()
    return EvaluationResponse(locked=True, evaluation=snap, public_summary=public)