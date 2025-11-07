from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/session", tags=["session"])

@router.get("/summary")
def summary(req: Request):
    s = req.state.session
    return {
        "keys": list(s["answers"].keys()),
        "flavor_keys": list(s["flavor"].keys()),
        "yap_summary": s.get("yap_summary", []),
        "vibe": s.get("vibe"),
        "evaluation_locked": s.get("evaluation_locked"),
        "flavor_locked": s.get("flavor_locked"),
    }

@router.get("/payload")
def payload(req: Request):
    s = req.state.session
    return {
        "profile": s.get("evaluation"),
        "flavor_profile": s.get("flavor_template"),
        "analysis": s.get("analysis"),
        "yap_summary": "; ".join(s.get("yap_summary", [])),
        "vibe": s.get("vibe"),
    }