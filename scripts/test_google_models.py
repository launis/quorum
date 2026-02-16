
import os
import sys
from dotenv import load_dotenv
from google.cloud import aiplatform, aiplatform_v1
from google.api_core import client_options
from google.api_core.exceptions import PermissionDenied, NotFound

# Load env including GOOGLE_APPLICATION_CREDENTIALS
load_dotenv(override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
SOURCE_LOCATION = "us-west1" # User suggested us-west works
TARGET_LOCATION = os.getenv("VERTEX_LOCATION", "europe-north1") # Local Execution Region

if not PROJECT_ID:
    print("❌ GOOGLE_CLOUD_PROJECT not found in .env")
    sys.exit(1)

def list_foundation_models():
    """Dynamically discover models from Google source of truth (us-central1)."""
    print(f"\n🔍 Discovering Foundation Models from {SOURCE_LOCATION}...")
    
    try:
        # Use regional endpoint for US-Central1
        options = client_options.ClientOptions(
            api_endpoint=f"{SOURCE_LOCATION}-aiplatform.googleapis.com"
        )
        # Use GAPIC client directly for safety
        from google.cloud import aiplatform
        print(f"Aiplatform Version: {aiplatform.__version__}")
        client = aiplatform.gapic.ModelGardenServiceClient(client_options=options)
        print(f"Client methods: {[m for m in dir(client) if 'list' in m]}")
        
        # Parent resource for Google's own models
        parent = "publishers/google"
        
        # Fetch using kwargs (proto-plus support)
        try:
            response = client.list_publisher_models(parent=parent)
        except Exception as e:
            # Fallback: try passing dict
            print(f"  Debug: kwargs failed ({e}), trying dict...")
            response = client.list_publisher_models(request={"parent": parent})
        
        found_models = []
        for model in response:
            model_id = model.name.split("/")[-1]
            # Simple heuristic for relevant models
            if "gemini" in model_id.lower():
                found_models.append(model_id)
                
        print(f"✅ Found {len(found_models)} Gemini candidates in Source of Truth.")
        return sorted(found_models)

    except Exception as e:
        print(f"❌ Error listing models from {SOURCE_LOCATION}: {e}")
        # Suggest enabling API if PermissionDenied
        if "inclusive list of APIs" in str(e) or "not enabled" in str(e):
             print(f"👉 ACTION: Enable 'aiplatform.googleapis.com' for project {PROJECT_ID}")
        return []

def verify_target_region(models):
    """Check which models are actually deployable/usable in the Target region."""
    if not models:
        return

    print(f"\n🌍 Verifying execution availability in {TARGET_LOCATION}...")
    
    # We use a trick: Try to get the PublisherModel metadata from the REGIONAL endpoint.
    # If it exists, it's generally available.
    # Note: Foundation models are global resources but their endpoints are regional.
    # The 'GetPublisherModel' call might succeed even if not deployable.
    # A true test is 'BatchPrediction' or 'GenerateContent' availability, 
    # but that costs money/quota.
    # 
    # Better approach: The `ListPublisherModels` API is regional. 
    # Only models available in that region should be listed.
    # So we list again from Target Region!
    
    available_in_target = []
    
    try:
        options = client_options.ClientOptions(
            api_endpoint=f"{TARGET_LOCATION}-aiplatform.googleapis.com"
        )
        client = aiplatform_v1.ModelGardenServiceClient(client_options=options)
        parent = f"publishers/google"
        request = aiplatform_v1.ListPublisherModelsRequest(parent=parent)
        response = client.list_publisher_models(request=request)
        
        for model in response:
             model_id = model.name.split("/")[-1]
             if "gemini" in model_id.lower():
                 available_in_target.append(model_id)
                 
    except Exception as e:
        print(f"❌ Error checking target region {TARGET_LOCATION}: {e}")
        return

    # Compare
    print(f"{'Model ID':<40} | {'US-Central1':<10} | {TARGET_LOCATION:<10}")
    print("-" * 70)
    
    # Combine sets
    all_models = sorted(list(set(models + available_in_target)))
    
    for m in all_models:
        in_source = "✅" if m in models else "❌"
        in_target = "✅" if m in available_in_target else "❌"
        
        # Highlight discrepancies
        alert = ""
        if in_source == "✅" and in_target == "❌":
            alert = "(Not available locally!)"
            
        print(f"{m:<40} | {in_source:<10} | {in_target:<10} {alert}")

if __name__ == "__main__":
    print(f"Project: {PROJECT_ID}")
    print(f"Auth:    {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    source_models = list_foundation_models()
    if source_models:
        verify_target_region(source_models)
