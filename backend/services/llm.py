import os, json, re
import google.generativeai as genai
from backend.core.config import settings

def _model():
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError("Missing GOOGLE_API_KEY/GEMINI_API_KEY")
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    return genai.GenerativeModel("gemini-2.5-pro")

_WORD = re.compile(r"\b[\w’']+\b", re.UNICODE)

def limit_words(s: str, n: int = 100) -> str:
    if not s: return ""
    words = _WORD.findall(s)
    if len(words) <= n: return s.strip()
    taken, out, idx = 0, [], 0
    for m in _WORD.finditer(s):
        if taken >= n: break
        out.append(s[idx:m.end()]); idx = m.end(); taken += 1
    return "".join(out).rstrip()

def strip_fences(text: str) -> str:
    if not text: return ""
    t = text.strip()
    if "```json" in t: t = t.split("```json",1)[-1].split("```",1)[0]
    elif t.startswith("```"): t = t[3:].split("```",1)[0]
    return t.strip()

def call_json_strict(prompt: str, retry_once=True) -> dict:
    m = _model()
    try:
        resp = m.generate_content([{ "role":"user", "parts":[prompt] }])
        data = json.loads(strip_fences(resp.text))
        return data
    except Exception:
        if not retry_once: raise
        resp2 = m.generate_content([{ "role":"user", "parts":[prompt + "\nReturn JSON ONLY. Fix mistakes."] }])
        return json.loads(strip_fences(resp2.text))