import re, time
from typing import Dict, Any
from backend.schemas.evaluation import EvaluationSnapshot, CoreStats, Personality

def _to_cm(height: str|None) -> float|None:
    if not height: return None
    s = str(height).lower().strip().replace('"','')
    m = re.match(r"^\s*(\d)\s*'\s*(\d{1,2})\s*$", s)
    if m:
        feet, inch = int(m.group(1)), int(m.group(2))
        return round((feet*12 + inch) * 2.54, 0)
    m = re.match(r"^\s*([\d.]+)\s*cm\s*$", s)
    return float(m.group(1)) if m else None

def _to_kg(weight: str|None) -> float|None:
    if not weight: return None
    s = str(weight).lower().strip()
    m = re.match(r"^\s*([\d.]+)\s*lb[s]?\s*$", s)
    if m: return round(float(m.group(1)) * 0.453592, 1)
    m = re.match(r"^\s*([\d.]+)\s*kg\s*$", s)
    return float(m.group(1)) if m else None

def _rule_somatotype(a: Dict[str,Any]) -> str:
    bone = (a.get("bone_structure") or "").lower()
    muscle = (a.get("muscle_gain") or "").lower()
    fat = (a.get("fat_distribution") or "").lower()
    score = {"ecto":0,"meso":0,"endo":0}
    if "overlap" in bone or "slender" in bone: score["ecto"] += 2
    if "just touch" in bone or "medium" in bone: score["meso"] += 1
    if "don’t touch" in bone or "dont touch" in bone or "big frame" in bone: score["endo"] += 2
    if "fast" in muscle: score["meso"] += 2
    elif "extremely slow" in muscle or "barely" in muscle: score["ecto"] += 1
    if "belly" in fat: score["endo"] += 2
    if "evenly" in fat: score["meso"] += 1
    return {"ecto":"ectomorph","meso":"mesomorph","endo":"endomorph"}[max(score, key=score.get)]

def _rule_goal(a: Dict[str,Any]) -> str:
    carb = (a.get("carb_response") or "").lower()
    post = (a.get("post_meal_energy") or "").lower()
    muscle = (a.get("muscle_gain") or "").lower()
    if "knock" in carb or "sleepy" in post: return "fat_loss"
    if "fast" in muscle: return "muscle_gain"
    return "recomp"

def build_snapshot(session: Dict[str,Any]) -> EvaluationSnapshot:
    a = session["answers"]
    allergies = set()
    for k in ("allergies","dietary_restrictions"):
        v = a.get(k) or session["flavor"].get(k)
        if isinstance(v, list): allergies.update(v)
        elif isinstance(v, str) and v: allergies.add(v)

    somato = _rule_somatotype(a)
    goal = _rule_goal(a)

    core = CoreStats(
        name=a.get("name"),
        gender=a.get("gender"),
        age=int(a["age"]) if str(a.get("age","")).isdigit() else None,
        height_cm=_to_cm(a.get("height")),
        weight_kg=_to_kg(a.get("weight")),
        bone_structure=a.get("bone_structure"),
        fat_distribution=a.get("fat_distribution"),
        muscle_gain=a.get("muscle_gain"),
        carb_response=a.get("carb_response"),
        post_meal_energy=a.get("post_meal_energy"),
        flexibility=a.get("flexibility"),
        training_time=a.get("training_time"),
    )
    notes = []
    if any((x.lower()=="dairy" for x in allergies)): notes.append("Dairy-free")
    if core.training_time: notes.append(f"Training: {core.training_time}")

    snap = EvaluationSnapshot(
        somatotype=somato,
        fitness_goal=goal,
        core=core,
        persona=Personality(vibe_line=session.get("vibe"), style="concise"),
        constraints={"allergies": sorted(allergies), "dislikes": session["flavor"].get("dislikes", [])},
        notes=notes,
        version="v1",
        locked_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    return snap