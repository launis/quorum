import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Vertex AI credentials
google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("VERTEX_LOCATION", "europe-north1")

print(f"GOOGLE_APPLICATION_CREDENTIALS: {google_creds}")
print(f"GOOGLE_CLOUD_PROJECT: {project_id}")
print(f"VERTEX_LOCATION: {location}")

if not google_creds or not project_id:
    print("Error: Missing credentials in .env!")
    sys.exit(1)

try:
    import google.auth
    import google.auth.transport.requests
    from google.auth.transport.requests import Request as GRequest
    import google.cloud.aiplatform_v1 as aiplatform_v1
    import google.auth.credentials as g_client_options
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    print("\nGoogle SDK dependencies successfully loaded.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Authenticate
try:
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(GRequest())
    print(f"Authenticated successfully for GCP project: {project}")
except Exception as e:
    print(f"Authentication failed: {e}")
    sys.exit(1)

# Models to check
models_to_check = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3.1-flash",
    "gemini-3.1-pro",
    "gemini-3.5-flash",
    "gemini-3.5-pro"
]

print("\nChecking Vertex AI Model availability in region:", location)
api_endpoint = f"{location}-aiplatform.googleapis.com"

try:
    client = aiplatform_v1.ModelGardenServiceClient(
        client_options={"api_endpoint": api_endpoint}
    )
except Exception as e:
    print(f"Failed to create ModelGardenServiceClient: {e}")
    client = None

for m in models_to_check:
    print(f"\n[Model: {m}]")
    # 1. Test via SDK initialization
    try:
        vertexai.init(project=project, location=location, credentials=credentials)
        model = GenerativeModel(m)
        print("  - GenerativeModel initialization: OK")
    except Exception as e:
        print(f"  - GenerativeModel initialization: FAILED ({e})")

    # 2. Test via ModelGarden service API
    if client:
        try:
            resource_name = f"publishers/google/models/{m}"
            client.get_publisher_model(name=resource_name)
            print("  - ModelGarden registration check: AVAILABLE")
        except Exception as e:
            print(f"  - ModelGarden registration check: NOT AVAILABLE ({e})")
