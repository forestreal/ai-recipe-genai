from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session as OrmSession
from backend.schemas.flavor import FlavorAnswer, FlavorTemplate, FlavorLockRequest, FlavorLockResponse
from backend.models import Flavor as FlavorRow
import time

router = APIRouter(prefix="/api/flavor", tags=["flavor"])

@router.post("/answer")
def flavor_answer(req: Request, body: FlavorAnswer):
    s = req.state.session
    s["flavor"][body.question_id] = body.value
    return {"ok": True}

@router.post("/lock", response_model=FlavorLockResponse)
def flavor_lock(req: Request, body: FlavorLockRequest, db: OrmSession = Depends(...:=get_db)):
    s = req.state.session
    if s.get("flavor_locked") and not body.force:
        tmpl = s["flavor_template"]
    else:
        f = s["flavor"]
        ev = s.get("evaluation")
        tmpl = FlavorTemplate(
            cuisines=f.get("cuisines") or f.get("preferred_cuisines", []) or [],
            heat=f.get("heat"),
            herbs_spices=f.get("herbs_spices", []),
            preferred_proteins=f.get("preferred_proteins", []),
            avoidances=f.get("avoidances", []),
            allergies=list({*(f.get("allergies", []) or []), *((ev.constraints.get("allergies", []) if ev else []) )}),
            dislikes=list({*(f.get("dislikes", []) or []), *((ev.constraints.get("dislikes", []) if ev else []) )}),
            notes=f.get("notes", []),
            locked_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        s["flavor_template"] = tmpl
        s["flavor_locked"] = True
        db.add(FlavorRow(user_id=1, template=tmpl.model_dump(), locked=True))
        db.commit()
    return FlavorLockResponse(locked=True, flavor=tmpl)