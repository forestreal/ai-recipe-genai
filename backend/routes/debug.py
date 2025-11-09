from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.services.llm import call_json_strict, generate_fallback_response
import json

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.post("/generate")
async def debug_generate(req: Request):
    """Dev-only endpoint: generate recipes using the LLM when possible,
    otherwise return a deterministic fallback demo. No auth or session checks.
    Accepts optional JSON body: {count: int, meals: [str]}
    """
    body = {}
    try:
        body = await req.json()
    except Exception:
        body = {}

    count = int(body.get("count", 1))
    meals = body.get("meals", ["lunch"]) or ["lunch"]

    sys = (
        "You return STRICT JSON only: an array of recipes. No text outside JSON.\n"
        "Each recipe must include: title, cuisine, meal_type, prep_time, difficulty, "
        "ingredients[{item,quantity,unit}], instructions[], macros{calories,protein_g,carbs_g,fat_g,fiber_g}, "
        "micros_highlights[], timing, notes (≤40 words). Units: metric. Honor allergies as hard constraints.\n"
    )
    user = {"MEALS": meals, "COUNT": count}
    prompt = sys + "\n\nUSER:\n" + json.dumps(user, ensure_ascii=False)

    # Try real LLM first
    data = call_json_strict(prompt)
    if isinstance(data, dict) and data.get("error"):
        # Fall back to deterministic demo
        demo = generate_fallback_response(prompt)
        # Ensure we return a list with requested count
        if isinstance(demo, list):
            out = demo
        else:
            out = [demo]
        if len(out) == 1 and count > 1:
            out = out * count
        return out

    # If LLM returned non-list, try to coerce/wrap
    if not isinstance(data, list):
        data = [data] if isinstance(data, dict) else []

    # If the model returned fewer than requested, and it's likely the demo, fill
    if len(data) == 1 and count > 1:
        data = data * count

    return data
