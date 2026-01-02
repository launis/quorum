import os
import logging
from google.cloud import aiplatform_v1beta1
import google.auth
from google.api_core.exceptions import InvalidArgument, PermissionDenied, NotFound

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connectivity():
    print("Diagnostics: Testing Vertex AI Connectivity...")
    
    # Force load credentials from implicit environment if set (or file)
    creds, project_id = google.auth.default()
    print(f"Auth resolved Project ID: {project_id}")
    
    if not project_id:
        print("ERROR: No Project ID resolved.")
        return

    locations = ["us-central1", "europe-north1"]
    
    for loc in locations:
        print(f"\n--- Testing Location: {loc} ---")
        try:
            api_endpoint = f"{loc}-aiplatform.googleapis.com"
            client_options = {"api_endpoint": api_endpoint}
            client = aiplatform_v1beta1.ModelGardenServiceClient(client_options=client_options)
            
            parent = f"projects/{project_id}/locations/{loc}"
            
            # Simple list call
            response = client.list_publisher_models(parent=parent)
            print(f"SUCCESS: Connected to {loc}. Found {len(list(response.publisher_models))} models (first page).")
            
        except InvalidArgument as e:
            print(f"FAILURE ({loc}): Invalid Argument. This usually means the API is disabled or Project ID is invalid/deleted.")
            print(f"Details: {e}")
        except PermissionDenied as e:
            print(f"FAILURE ({loc}): Permission Denied. Service Account missing roles or Org Policy blocks this region.")
            print(f"Details: {e}")
        except NotFound as e:
            print(f"FAILURE ({loc}): Not Found. The resource does not exist.")
            print(f"Details: {e}")
        except Exception as e:
            print(f"FAILURE ({loc}): Unexpected Error: {e}")

if __name__ == "__main__":
    test_connectivity()
