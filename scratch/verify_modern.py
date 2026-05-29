import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Vertex AI credentials
google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("VERTEX_LOCATION", "us-central1")

print(f"GOOGLE_APPLICATION_CREDENTIALS: {google_creds}")
print(f"GOOGLE_CLOUD_PROJECT: {project_id}")
print(f"VERTEX_LOCATION: {location}")

if not google_creds or not project_id:
    print("Error: Missing credentials in .env!")
    sys.exit(1)

try:
    # Import the new, modern Google GenAI SDK (V2/2026 unified standard)
    from google import genai
    from google.genai import types
    print("\nModern google-genai SDK successfully loaded.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Authenticate and initialize client
try:
    # Explicitly set the credentials filepath in the environment so the client picks it up
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds
    
    # Initialize the modern Client with Vertex AI enabled
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )
    print(f"Modern Vertex AI Client initialized successfully for location: {location}")
except Exception as e:
    print(f"Failed to initialize modern Client: {e}")
    sys.exit(1)

# Models to verify
models_to_check = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3.1-flash",
    "gemini-3.1-pro",
    "gemini-3.5-flash",
    "gemini-3.5-pro"
]

print(f"\nVerifying models via modern Client in region: {location}")
for m in models_to_check:
    print(f"\n[Model: {m}]")
    try:
        # We perform a lightweight model check using get or list
        model_info = client.models.get(model=m)
        print(f"  - Model status: AVAILABLE")
        print(f"  - Input Token Limit: {model_info.input_token_limit}")
        print(f"  - Output Token Limit: {model_info.output_token_limit}")
    except Exception as e:
        print(f"  - Model status: NOT AVAILABLE ({e})")
