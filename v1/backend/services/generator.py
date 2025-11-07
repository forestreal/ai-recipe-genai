import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Any

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_genai_llm(prompt: str, model="gemini-2.5-pro-preview-06-05") -> Dict[str, Any]:
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt)
    return json.loads(response.text)

