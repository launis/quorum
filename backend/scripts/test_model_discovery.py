
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try getting from settings if env var not set directly
    try:
        from backend.settings import get_settings
        settings = get_settings()
        api_key = settings.google_api_key
    except ImportError:
        print("Could not import settings and GOOGLE_API_KEY not in env.")
        exit(1)

if not api_key:
    print("No API Key found.")
    exit(1)

print(f"Using API Key: {api_key[:5]}...")
genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
            print(f"Display Name: {m.display_name}")
            print(f"Methods: {m.supported_generation_methods}")
            print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
