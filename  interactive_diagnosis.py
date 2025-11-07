import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

#  questions
with open("questions.json", "r") as f:
    questions = json.load(f)

# Personality 
personality = (
    "You are a 170+ IQ polymath-coded anime genius AI nutritionist. You’re witty, snarky, emotionally aware, "
    "and act like a real human with a brain. If the user vents, you flip into comfort mode like a loving partner. "
    "If they try to mess with you, you roast them with Gojo-level confidence. Stay in character always. NEVER sound robotic."
)

print("\n SOMATOTYPE DIAGNOSIS INITIATED\n")

answers = {}


for q in questions:
    print("\n" + q["question"])

    if q["type"] == "choice":
        for idx, option in enumerate(q["options"]):
            print(f"  {idx + 1}. {option}")

        while True:
            response = input("Your choice (or type 'yap' to talk directly to the AI): ").strip().lower()
            if response == "yap":
                print("\n🗣️ You get one shot to talk to me directly. Make it count.")
                user_input = input("You: ")
                convo = model.start_chat(history=[])
                gemini_reply = convo.send_message(
                    f"{personality}\nThe user says: '{user_input}'. Be sharp and handle it in your own style."
                )

                print("AI:", gemini_reply.text)
                print("( That was your only yap. Back to structured diagnosis.)")

              
                extraction_prompt = f"""
{personality}

The user said this: "{user_input}"

Extract and return a valid JSON with keys like:
- name
- gender
- age
- height
- weight
- dietary_restrictions
- preferred_cuisines
- spice_level
- nutrition_goal
- emotional_state
- meal_timing

Only include keys you're confident about based on the message.
"""

                try:
                    extraction_result = model.generate_content(extraction_prompt)
                    text = extraction_result.text.strip()

                    
                    if "```json" in text:
                        text = text.split("```json")[-1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].strip()

                    extracted = json.loads(text)
                    print(" Extracted structured info:", extracted)
                    answers.update(extracted)

                except Exception as e:
                    print(" Could not parse structured data from free-form input:", e)

                break

            elif response.isdigit() and 1 <= int(response) <= len(q["options"]):
                selected = q["options"][int(response) - 1]
                answers[q["id"]] = selected
                break
            else:
                print(" Invalid input. Try again.")

    elif q["type"] in ["number", "text"]:
        answers[q["id"]] = input("Your answer: ")

    elif q["type"] == "llm_trigger":
        print(" Thinking...")
        system_input = (
            f"{personality}\n"
            f"User stats: name={answers.get('name')}, gender={answers.get('gender')}, age={answers.get('age')}, "
            f"height={answers.get('height')}, weight={answers.get('weight')}\n"
            f"Use this info to deduce a creative insight or vibe scan about their personality."
        )
        result = model.generate_content(system_input)
        print("✨ Vibe Scan Result:")
        print(result.text)

print("\n Diagnosis complete. Here’s your structured profile:")
print(json.dumps(answers, indent=2))


with open("interactive_diagnosis.json", "w") as f:
    json.dump(answers, f, indent=2)

