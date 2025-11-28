import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    with open("models_list.txt", "w") as f:
        f.write("GOOGLE_API_KEY not found in environment.")
else:
    genai.configure(api_key=api_key)
    try:
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        with open("models_list.txt", "w") as f:
            f.write("\n".join(models))
    except Exception as e:
        with open("models_list.txt", "w") as f:
            f.write(f"Error listing models: {e}")
