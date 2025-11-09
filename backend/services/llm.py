import os, json, re
import google.generativeai as genai
from backend.core.config import settings

# Cache the model to avoid re-initialization
_model_cache = None
_fallback_mode = False  # Track if we're in fallback mode
_last_api_key = None  # Track the last API key used

def _model():
    global _model_cache, _fallback_mode, _last_api_key
    
    api_key = settings.GOOGLE_API_KEY
    # Clean up the API key (remove any whitespace, quotes)
    if api_key:
        api_key = str(api_key).strip().strip('"').strip("'")
    
    # Check if API key is set and not a placeholder
    if not api_key or str(api_key).strip() in ["your-api-key-here", "", "None", "null"]:
        _fallback_mode = True
        if _model_cache is None:  # Only log once
            print("⚠️  API key not configured - using fallback mode (mock responses)")
        return None  # Signal fallback mode
    
    # Auto-fix: If key starts with "IzaSy" instead of "AIzaSy", add "AI" prefix
    if api_key.startswith("IzaSy") and not api_key.startswith("AIzaSy"):
        api_key = "AI" + api_key
        print(f"⚠️  Auto-fixed API key (added missing 'AI' prefix)")
    
    # If API key changed, reset cache
    if _last_api_key != api_key:
        _model_cache = None
        _fallback_mode = False
        _last_api_key = api_key
        print(f"🔄 API key changed, reinitializing Gemini model...")
    
    # Return cached model if available and not in fallback mode
    if _model_cache is not None and not _fallback_mode:
        return _model_cache
    
    # Try to configure and initialize the API
    try:
        genai.configure(api_key=api_key)
        # Create and cache the model
        _model_cache = genai.GenerativeModel("gemini-2.5-pro")
        _fallback_mode = False
        _last_api_key = api_key
        print("✅ Google Gemini API initialized successfully")
        return _model_cache
    except Exception as e:
        error_msg = str(e)
        # Check for specific API key errors
        if any(keyword in error_msg.lower() for keyword in ["api_key", "api key", "invalid", "unauthorized", "permission", "403", "401", "400"]):
            _fallback_mode = True
            _model_cache = None
            print(f"⚠️  API key error - using fallback mode: {error_msg[:150]}")
            return None  # Signal fallback mode
        # For other errors, still try fallback but log the error
        _fallback_mode = True
        _model_cache = None
        print(f"⚠️  API initialization failed - using fallback mode: {error_msg[:150]}")
        return None

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

def _generate_fallback_response(prompt: str) -> dict:
    """Generate a fallback mock response when API key is unavailable"""
    prompt_lower = prompt.lower()
    
    # Try to detect what kind of response is needed
    if "yap" in prompt_lower or "public_reply" in prompt_lower:
        # Yap chat response
        return {
            "public_reply": "I'm in demo mode right now! To get real AI responses, please configure your Google Gemini API key. Check SETUP_API_KEY.md for instructions. But hey, I'm still here to chat! 😊",
            "tone": "neutral",
            "relation": "none",
            "deduction": {},
            "model_notes": "Fallback mode - API key not configured"
        }
    elif "analysis" in prompt_lower or "culinary" in prompt_lower:
        # Analysis response
        return {
            "version": "1.0",
            "core_attributes": {"creativity": "moderate", "adventure": "moderate"},
            "leaning_cuisines": ["Mediterranean", "Asian fusion"],
            "cooking_styles": ["balanced", "health-conscious"],
            "ingredient_bias": {"fresh": "high", "processed": "low"},
            "taste_notes": "Balanced flavors with preference for fresh ingredients",
            "summary": "Demo mode: Configure API key for personalized analysis. Your culinary profile shows balanced preferences."
        }
    elif "recipe" in prompt_lower or "recipes" in prompt_lower:
        # Recipe generation response - return as array to match expected format
        return [
            {
                "title": "Demo Recipe (Configure API Key)",
                "cuisine": "Demo",
                "meal_type": "lunch",
                "prep_time": "15 min",
                "difficulty": "easy",
                "ingredients": [{"item": "Demo ingredient 1", "quantity": 1, "unit": "cup"}],
                "instructions": ["Step 1: Configure your Google Gemini API key in .env", "Step 2: Restart the API container", "Step 3: Get real AI-generated recipes!"],
                "macros": {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0},
                "micros_highlights": [],
                "timing": "Demo mode",
                "notes": "This is a placeholder. Configure GOOGLE_API_KEY for real recipes!"
            }
        ]
    else:
        # Generic fallback
        return {
            "message": "Demo mode active. Configure GOOGLE_API_KEY in .env for real AI responses.",
            "status": "fallback",
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt
        }


def generate_fallback_response(prompt: str) -> dict:
    """Public wrapper for generating a fallback response from the LLM service.
    This is useful for routes which want to return a deterministic demo reply
    when the Gemini API is unavailable or is taking too long.
    """
    return _generate_fallback_response(prompt)

def call_json_strict(prompt: str, retry_once=True) -> dict:
    """
    Call Gemini API with strict JSON output.
    If GOOGLE_API_KEY is missing, returns {"error": "Missing Google API key"}.
    Wraps Gemini API calls and returns {"error": str(e)} on failure instead of raising.
    """
    # If GOOGLE_API_KEY is missing, return clear JSON error
    api_key = settings.GOOGLE_API_KEY
    if not api_key or str(api_key).strip() in ["your-api-key-here", "", "None", "null"]:
        return {"error": "Missing Google API key"}

    # Try to get a model instance
    try:
        m = _model()
    except Exception as e:
        return {"error": f"Model initialization error: {str(e)}"}

    if m is None:
        # If model is None here, something went wrong during initialization
        return {"error": "Unable to initialize Gemini model"}

    # We have a valid model - use Gemini API (wrap in try/except)
    try:
        resp = m.generate_content([{ "role":"user", "parts":[prompt] }])
    except Exception as e:
        return {"error": str(e)}

    # Validate response
    try:
        if not resp or not getattr(resp, 'text', None):
            return {"error": "Empty response from Gemini API"}
        data = json.loads(strip_fences(resp.text))
        return data
    except json.JSONDecodeError as e:
        # Try one retry with stricter instruction
        if retry_once:
            try:
                resp2 = None
                try:
                    resp2 = m.generate_content([{ "role":"user", "parts":[prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no extra text."] }])
                except Exception as e2:
                    return {"error": f"API retry failed: {str(e2)}"}
                if resp2 and getattr(resp2, 'text', None):
                    try:
                        data = json.loads(strip_fences(resp2.text))
                        return data
                    except Exception as e3:
                        return {"error": f"JSON parse error after retry: {str(e3)}"}
            except Exception as e:
                return {"error": f"JSON parse/retry error: {str(e)}"}
        return {"error": f"JSON parse error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}