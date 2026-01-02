from google.cloud import aiplatform
import google.auth
import os

def check():
    print("--- Inference Access Check ---")
    try:
        _, project = google.auth.default()
        print(f"Project resolved from ADC: {project}")
    except Exception as e:
        print(f"Auth failed: {e}")
        return

    # Check both regions
    for loc in ["europe-north1", "us-central1"]:
        print(f"\nChecking region: {loc}")
        try:
            # We use the high-level SDK 'init' which validates basic config
            aiplatform.init(project=project, location=loc)
            
            # Simple API call: List custom models (not Publisher models)
            # This verifies the API is enabled and accessible in this region.
            models = aiplatform.Model.list()
            print(f"  SUCCESS: Connected to {loc}. API is working. (Custom models count: {len(models)})")
            
        except Exception as e:
            print(f"  FAILURE: Could not access {loc}.")
            print(f"  Error: {e}")

if __name__ == "__main__":
    check()
