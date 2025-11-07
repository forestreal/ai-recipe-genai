from fastapi import APIRouter, Request, HTTPException
from backend.schemas.yap import YapRequest, YapPublicResponse
from backend.services.llm import call_json_strict, limit_words
from backend.redisx import incr_and_check
import json, re

router = APIRouter(prefix="/api/yap", tags=["yap"])

ALLOWED_EXTRA = {"allergies","dislikes","cuisines","training_time","spice_level","dietary_restrictions"}

def _norm_height(v: str) -> str:
    if not v: return v
    s = str(v).lower().strip().replace('"','')
    m = re.match(r"^\s*(\d)\s*'\s*(\d{1,2})\s*$", s)
    if m:
        cm = round((int(m.group(1))*12 + int(m.group(2))) * 2.54)
        return f"{cm} cm"
    if s.endswith("cm"):
        try: return f"{int(round(float(s[:-2].strip())))} cm"
        except: return v
    return v

def _norm_weight(v: str) -> str:
    if not v: return v
    s = str(v).lower().strip()
    m = re.match(r"^\s*([\d.]+)\s*lb[s]?\s*$", s)
    if m: return f"{round(float(m.group(1))*0.453592,1)} kg"
    m = re.match(r"^\s*([\d.]+)\s*kg\s*$", s)
    if m: return f"{float(m.group(1))} kg"
    return v

def _apply_commit(session, q, ded) -> list[str]:
    applied = []
    answers = session["answers"]
    fq = (ded or {}).get("for_question") or {}
    if fq.get("id") == q["id"]:
        val = fq.get("value")
        if q["id"] == "height": val = _norm_height(val)
        if q["id"] == "weight": val = _norm_weight(val)
        if q["type"] == "choice" and q.get("options"):
            if fq.get("option_chosen") in q["options"]:
                answers[q["id"]] = fq["option_chosen"]; applied.append(q["id"])
            elif fq.get("new_option"):
                answers[q["id"]] = fq["new_option"]; applied.append(q["id"])
        else:
            if val is not None: answers[q["id"]] = val; applied.append(q["id"])

    for ex in ((ded or {}).get("extras") or []):
        i = ex.get("id"); v = ex.get("value"); op = ex.get("op","set")
        if i not in ALLOWED_EXTRA: continue
        if op == "append_unique":
            cur = answers.get(i, [])
            if not isinstance(cur, list): cur = [cur] if cur else []
            if v not in cur: cur.append(v)
            answers[i] = cur
        else:
            answers[i] = v
        applied.append(i)
    session["yap_summary"] = list(dict.fromkeys(session.get("yap_summary", [])))
    return list(dict.fromkeys(applied))

@router.post("/answer", response_model=YapPublicResponse)
async def yap_answer(req: Request, body: YapRequest):
    # Rate-limit
    ip = req.client.host if req.client else "unknown"
    if not incr_and_check(ip, "yap", 30, 60):
        raise HTTPException(status_code=429, detail="Too many requests")

    session = req.state.session
    system = (
      "You are a polymath nutritionist with anime-coded, PG snark. "
      "Return JSON ONLY with keys: public_reply, tone, relation, deduction, model_notes. "
      "public_reply ≤100 words. If food-related → polymath; if trolling → snark; if sad → gentle; else neutral/disregard. "
      "Silently deduce normalized value for CURRENT QUESTION; choose existing option or propose new one; "
      "You MUST NOT reveal extracted values."
    )

    user_block = {
      "CURRENT QUESTION": body.question.model_dump(),
      "USER FREE TEXT": body.user_message,
      "CONTEXT": {"answers_so_far": session["answers"], "flavor_so_far": session["flavor"]}
    }
    prompt = system + "\n\n" + json.dumps(user_block, ensure_ascii=False)
    data = call_json_strict(prompt)

    public = limit_words(data.get("public_reply",""), 100)
    tone = data.get("tone","neutral")
    relation = data.get("relation","none")
    ded = (data.get("deduction") or {})
    applied = _apply_commit(session, body.question.model_dump(), ded)

    return YapPublicResponse(
        display_reply=public,
        tone=tone,
        relation=relation,
        commit={"applied": bool(applied), "ids": applied}
    )