import asyncio
# formatted: minor whitespace/formatting update (non-functional)
import logging
import time
from backend.core.config import settings
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from backend.schemas.yap import YapRequest, YapPublicResponse
from backend.services.llm import call_json_strict, limit_words, generate_fallback_response
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

    # ensure logger exists
    logger = logging.getLogger(__name__)

    # 0) Ensure the API key is present before doing anything networky
    # Prefer the app settings; avoid directly using os.getenv here so
    # we don't raise NameError if os isn't available in reload races.
    gkey = getattr(settings, "GOOGLE_API_KEY", None)
    if not gkey:
        logger.warning("Missing GOOGLE_API_KEY in environment")
        # 503 Service Unavailable is appropriate for missing external credentials
        return JSONResponse(status_code=503, content={"error": "Missing GOOGLE_API_KEY in environment"})

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
      "CONTEXT": {"answers_so_far": session.get("answers", []), "flavor_so_far": session.get("flavor", {})}
    }
    prompt = system + "\n\n" + json.dumps(user_block, ensure_ascii=False)

    # 1) Call the LLM with a timeout and robust error handling.
    # Timeout is configurable via settings.LLM_TIMEOUT (seconds).
    timeout_seconds = int(getattr(settings, "LLM_TIMEOUT", 60))
    try:
        logger.debug("LLM request starting (timeout=%ss)", timeout_seconds)
        t0 = time.monotonic()
        # If call_json_strict is synchronous, run in threadpool; if async, await directly.
        if asyncio.iscoroutinefunction(call_json_strict):
            data = await asyncio.wait_for(call_json_strict(prompt), timeout=timeout_seconds)
        else:
            # run blocking call in thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            data = await asyncio.wait_for(loop.run_in_executor(None, call_json_strict, prompt), timeout=timeout_seconds)
        took = time.monotonic() - t0
        logger.debug("LLM request completed in %.2fs", took)
    except asyncio.TimeoutError:
        logger.exception("LLM call timed out after %ss", timeout_seconds)
        # Use a deterministic fallback response so the endpoint doesn't 504.
        try:
            data = generate_fallback_response(prompt)
            logger.info("Returned fallback response after timeout")
        except Exception as e:
            logger.exception("Fallback generation failed: %s", e)
            return JSONResponse(status_code=504, content={"error": "LLM request timed out and fallback failed"})
    except Exception as e:
        logger.exception("LLM call failed")
        # 502 Bad Gateway or 503 depending on whether you treat this as upstream failure
        return JSONResponse(status_code=502, content={"error": "LLM request failed", "detail": str(e)})

    # 2) If the LLM returned an error object, return JSON error instead of crashing
    if isinstance(data, dict) and data.get("error"):
        logger.warning("LLM returned an error object: %s", data.get("error"))
        return JSONResponse(status_code=503, content={"error": data.get("error")})

    # 3) Validate the shape of the returned data defensively
    if not isinstance(data, dict):
        logger.error("Unexpected LLM response type: %s", type(data))
        return JSONResponse(status_code=502, content={"error": "Unexpected LLM response format"})

    public = limit_words(data.get("public_reply",""), 100)
    tone_raw = (data.get("tone") or "neutral").strip()
    relation_raw = (data.get("relation") or "none").strip()

    # Normalize LLM outputs to the allowed literal choices in YapPublicResponse
    allowed_tones = {"polymath", "snark", "gentle", "neutral", "disregard"}
    # LLM may return combined values like "neutral/disregard" or variants — pick the first allowed token
    tone = tone_raw
    if tone not in allowed_tones:
        # try splitting on common separators
        for sep in ["/", ",", ";", " "]:
            parts = [p.strip() for p in tone_raw.split(sep) if p.strip()]
            picked = next((p for p in parts if p in allowed_tones), None)
            if picked:
                tone = picked
                break
    if tone not in allowed_tones:
        tone = "neutral"

    allowed_rel = {"related", "offtopic", "none"}
    relation = relation_raw
    if relation not in allowed_rel:
        # map ambiguous terms to 'none'
        if relation_raw.lower() in ("neutral", "irrelevant", "unrelated"):
            relation = "none"
        else:
            # try splitting
            for sep in ["/", ",", ";", " "]:
                parts = [p.strip() for p in relation_raw.split(sep) if p.strip()]
                picked = next((p for p in parts if p in allowed_rel), None)
                if picked:
                    relation = picked
                    break
    if relation not in allowed_rel:
        relation = "none"
    ded = (data.get("deduction") or {})
    applied = _apply_commit(session, body.question.model_dump(), ded)

    # success
    return YapPublicResponse(
        display_reply=public,
        tone=tone,
        relation=relation,
        commit={"applied": bool(applied), "ids": applied}
    )