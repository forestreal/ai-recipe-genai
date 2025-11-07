import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")


personality = (
    "You're a 170+ IQ polymath-coded anime nutritionist. Witty, emotionally intuitive, scientifically elite. "
    "When users are emotional, you're gentle and warm like a partner. When they're vague or lazy, you roast like Gojo. "
    "But your mission is to create powerful, structured, highly personalized nutrition blueprints."
)


async def call_genai_llm(prompt: str):
    full_prompt = (
        f"{personality}\n"
        f"Generate 5 beautiful, healthy recipes tailored to this user profile and dietary goals.\n"
        f"Each recipe must be returned as a JSON object with the following fields:\n"
        f"  - name (str)\n"
        f"  - type (e.g., breakfast, snack, etc.)\n"
        f"  - cuisine (e.g., Japanese, Italian, etc.)\n"
        f"  - ingredients (list of {{ ingredient name, quantity }})\n"
        f"  - instructions (step-by-step list)\n"
        f"  - calories (number)\n"
        f"  - macros ({{ protein, carbs, fat }})\n"
        f"  - micros ({{ vitamins, minerals }})\n"
        f"  - user_info (dict with basic user profile info like gender, age, height, weight, etc.)\n"
        f"Add a poetic or emotional flair to each recipe description — but do NOT include that as a field. Just keep it in the instructions section if needed.\n"
        f"\nReturn a JSON list of exactly 5 recipe objects. Do NOT wrap it in Markdown or extra text.\n\n"
        f"User profile:\n{prompt}"
    )

    convo = model.start_chat(history=[])
    res = convo.send_message(full_prompt)

    try:
        recipes_json = json.loads(res.text)
        return recipes_json
    except json.JSONDecodeError:
        fallback_prompt = (
            f"{personality}\nYou failed to return clean JSON. Regenerate ONLY the JSON array of 5 recipe objects. No markdown, no commentary, no headings."
        )
        retry = convo.send_message(fallback_prompt)
        try:
            return json.loads(retry.text)
        except json.JSONDecodeError:
            return {"error": "LLM response could not be parsed as valid JSON."}


