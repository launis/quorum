"""Debug Handler Discovery Tool."""
import os

from dotenv import load_dotenv

from backend.database.wrapper import get_db_client
from backend.llm.handler import LLMHandler

# Explicitly load dotenv like main.py likely does (or check if it happens automatically)
load_dotenv()

print("--- DIAGNOSTICS ---")
env_loc = os.getenv("VERTEX_LOCATION")
print(f"os.getenv('VERTEX_LOCATION'): '{env_loc}'")

handler = LLMHandler(get_db_client())

print("\n--- FETCHING MODELS (Default/Env) ---")
try:
    models = handler.fetch_all_available_models(providers=["google"])
    google_models = models.get("google", [])

    with open("valid_models_utf8.txt", "w", encoding="utf-8") as f:
        f.write(f"AVAILABLE GOOGLE MODELS in '{os.getenv('VERTEX_LOCATION')}':\n")
        for m in google_models:
            f.write(f" - {m}\n")

    if not google_models:
        print("❌ NO MODELS FOUND!")
    else:
        print(f"✅ Found {len(google_models)} models. Written to valid_models_utf8.txt")

except Exception as e:
    print(f"Error: {e}")
