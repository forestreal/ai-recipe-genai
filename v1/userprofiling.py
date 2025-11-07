

import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="/Users/meenav/ai-recipe-genai/.env")


load_dotenv()

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
    return response.text

# Example usage (replace with real user_answers when integrated):
if __name__ == "__main__":
    dummy_input = {
        "name": "Meena",
        "gender": "Female",
        "age": 21,
        "height": "5'9",
        "weight": "66.7 kgs",
        "weight_gain": "I gain slowly unless I overeat junk.",
        "weight_loss": "I lose weight quickly.",
        "bone_structure": "They overlap easily — definitely slender.",
        "carb_response": "They fill me up and I feel okay.",
        "post_meal_energy": "I feel normal — no change.",
        "fat_distribution": "Evenly all over",
        "muscle_gain": "Takes time, but eventually shows.",
        "flexibility": "Yes, with zero effort."
    }
    result = classify_user_profile(dummy_input)
    print("\n🔬 Classification Result:")
    print(result)