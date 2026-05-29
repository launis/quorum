import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Vertex AI credentials
google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("VERTEX_LOCATION", "global")

print(f"GOOGLE_APPLICATION_CREDENTIALS: {google_creds}")
print(f"GOOGLE_CLOUD_PROJECT: {project_id}")
print(f"VERTEX_LOCATION: {location}")

try:
    from google import genai
    from google.genai import types
    print("\nModern google-genai SDK loaded.")
except ImportError as e:
    print(f"Import Error: {e}")
    exit(1)

try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )
    print("Modern Vertex AI Client initialized.")
except Exception as e:
    print(f"Failed to initialize client: {e}")
    exit(1)

prompt = (
    "Explain in Finnish (exactly two concise paragraphs) how your advanced Gemini 3.5 Pro "
    "reasoning engine solves complex software architecture and strict code audit tasks "
    "compared to previous models."
)

# 1. Test gemini-3.5-flash first to verify modern client query works
print("\n[Testing gemini-3.5-flash via modern SDK...]")
try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    print("=== SUCCESS: RESPONSE FROM GEMINI 3.5 FLASH ===")
    print(response.text)
    print("===============================================")
except Exception as e:
    print(f"Failed to query gemini-3.5-flash: {e}")

# 2. Test gemini-3.5-pro via modern SDK
print("\n[Testing gemini-3.5-pro via modern SDK...]")
try:
    response = client.models.generate_content(
        model="gemini-3.5-pro",
        contents=prompt
    )
    print("=== SUCCESS: RESPONSE FROM GEMINI 3.5 PRO ===")
    print(response.text)
    print("=============================================")
except Exception as e:
    print(f"Failed to query gemini-3.5-pro: {e}")
