import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/meenav/ai-recipe-genai/.env")
genai.configure(api_key=os.getenv("AIzaSyA61rvrFPwL_AvuaaJqsmOeULzrfqt8uzk"))
model = genai.GenerativeModel("gemini-2.5-pro")

def classify_user_profile(user_answers):
    prompt = f"""
    You are a polymathic, nutritionist-coded LLM with a razor-sharp anime-coded personality.
    The user has filled out a detailed somatotype diagnostic questionnaire. Your job is to classify them into:
    - One of the 3 somatotypes (ectomorph, mesomorph, endomorph)
    - One broad fitness goal (e.g. fat loss, lean bulking, recomposition, maintenance)

    Analyze thoroughly and return a JSON response like:
    {{
      "somatotype": "ectomorph",
      "fitness_goal": "lean bulking",
      "notes": "High metabolism with poor muscle retention. Recommend progressive overload + caloric surplus."
    }}

    Here is the user's input:
    {json.dumps(user_answers, indent=2)}
    """
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except Exception:
        return {"error": "LLM failed to return valid JSON."}
