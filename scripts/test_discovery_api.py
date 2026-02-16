
import os
import sys
from dotenv import load_dotenv
from googleapiclient import discovery
import google.auth

# Load env
load_dotenv(override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
SOURCE_LOCATION = "us-west1" # User suggestion: Try us-west1

def test_discovery():
    print(f"Testing Discovery API for {PROJECT_ID} in {SOURCE_LOCATION}...")
    
    try:
        # Use Application Default Credentials
        credentials, project = google.auth.default()
        
        # Build service with explicit discovery URL for Vertex AI
        service = discovery.build(
            "aiplatform", 
            "v1", 
            credentials=credentials,
            discoveryServiceUrl=f"https://{SOURCE_LOCATION}-aiplatform.googleapis.com/$discovery/rest?version=v1"
        )
        
        # Full resource path for v1
        parent = f"projects/{PROJECT_ID}/locations/{SOURCE_LOCATION}/publishers/google"
        
        models_resource = service.projects().locations().publishers().models()
        # Debug methods
        print(f"Methods on models resource: {[m for m in dir(models_resource) if not m.startswith('_')]}")
        
        request = models_resource.list(parent=parent)
        response = request.execute()
        
        models = response.get("publisherModels", [])
        print(f"✅ Found {len(models)} models.")
        
        geminis = [m['name'].split('/')[-1] for m in models if "gemini" in m['name'].lower()]
        print(f"Gemini Models: {sorted(list(set(geminis)))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_discovery()
