
import os
import google.auth
from google.auth.transport.requests import Request
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
TARGET_LOCATION = os.getenv("VERTEX_LOCATION", "europe-north1")

def test_regional_check():
    print(f"Testing Model Availability in {TARGET_LOCATION}...")
    
    try:
        # Get Credentials
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        credentials.refresh(Request())
        token = credentials.token
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test Models
        test_models = ["gemini-1.5-pro", "gemini-1.0-pro", "non-existent-model"]
        
        for model in test_models:
            # Endpoint: GetPublisherModel
            # https://{location}-aiplatform.googleapis.com/v1/publishers/google/models/{model}
            url = f"https://{TARGET_LOCATION}-aiplatform.googleapis.com/v1/publishers/google/models/{model}"
            
            print(f"Checking {model}...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ {model} is AVAILABLE in {TARGET_LOCATION}")
            elif response.status_code == 404:
                print(f"❌ {model} is NOT FOUND in {TARGET_LOCATION}")
            else:
                print(f"⚠️ {model} returned {response.status_code}: {response.text[:100]}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_regional_check()
