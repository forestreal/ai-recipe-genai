import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

def flavor_deduction_engine(user_data, somatotype="", fitness_goal="", bmi=""):
    personality = """
    You are a polymathic LLM chef-therapist hybrid: a Michelin-star mind fused with anime-coded charm.
    You roast nonsense, gently console emotional rants like a genius boyfriend/girlfriend, and analyze like a gourmet-trained flavor savant.
    Always use prior context: name, age, gender, and preferences.
    Generate structured output. Be bold, smart, poetic, and playful — never robotic.
    """

    prompt = f"""
    Context:
    Name: {user_data.get('name')}
    Gender: {user_data.get('gender')}
    Age: {user_data.get('age')}
    Somatotype: {somatotype}
    Fitness Goal: {fitness_goal}
    BMI: {bmi}

    User answered the flavor profiling diagnostic.
    Use their free-form responses, allergy data, cuisine taste, and descriptive choices to deduce:

    1. A precise 1-2 word taste label for the user (e.g., "Citrus Seeker", "Umami Hunter", "Cozy Craver").
    2. List of ideal flavor notes (e.g., tangy, smoky, creamy).
    3. Culinary summary based on their personality and vibe.
    4. Personality remark (based on their answers and identity — playful, analytical, observant, curious, etc.).
    5. Roast or warmth depending on tone of their inputs (get creative).
    6. Recommended recipe types (3–5 total) that match everything above.
    7. Be poetic or sarcastic when needed, but always feel human and sharp.

    USER FLAVOR PROFILE INPUT:
    {json.dumps(user_data, indent=2)}
    """

    response = model.generate_content(f"{personality}\n{prompt}")
    return response.text

# Example usage
if __name__ == "__main__":
    user_data = {
        "name": "Meena",
        "gender": "Female",
        "age": 21,
        "cuisine_preferences": ["Italian", "Mexican", "Middle Eastern"],
        "allergies": ["None"],
        "avoid": "I hate eggplant. And don’t you dare sneak in raisins.",
        "flavor_craving": "Savory/Umami",
        "spice_tolerance": "I love intense spice — bring the fire",
        "favorite_dish": "Shakshuka with herbed sourdough",
        "fermented_likes": "Yes, I love them (kimchi, miso, sauerkraut)",
        "herb_profile": "Sharp & Asian (lemongrass, Thai basil, mint)",
        "comfort_food": "Warm and spicy",
        "dietary_style": "Balanced omnivore"
    }

    result = flavor_deduction_engine(user_data, somatotype="ectomorph", fitness_goal="lean bulking", bmi="21.5")
    print("\n🍲 FLAVOR PROFILE RESULT:\n")
    print(result)
