
import os
import google.auth
from google.auth.transport.requests import Request
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
SOURCE_LOCATION = "us-central1"

def test_raw_rest():
    print(f"Testing Raw REST API for {PROJECT_ID} in {SOURCE_LOCATION}...")
    
    try:
        # Get Credentials
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        credentials.refresh(Request())
        token = credentials.token
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # URLs to try
        urls = [
            # Global Endpoint (sometimes works for discovery)
            f"https://aiplatform.googleapis.com/v1/publishers/google/models",
            
            # Full path us-west1
            f"https://us-west1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-west1/publishers/google/models",
            
            # Full path us-central1 (for completeness)
            f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models",
        ]

        for url in urls:
            print(f"GET {url}")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("publisherModels", [])
                print(f"✅ Success with {url}")
                print(f"✅ Found {len(models)} models.")
                
                geminis = []
                for m in models:
                    mid = m.get("name", "").split("/")[-1]
                    if "gemini" in mid.lower():
                        geminis.append(mid)
                
                print(f"Gemini Models: {sorted(list(set(geminis)))}")
                return # Stop on first success
            else:
                print(f"❌ Failed: {response.status_code} - {response.text[:100]}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_raw_rest()
