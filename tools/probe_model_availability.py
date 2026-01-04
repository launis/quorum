import os
import logging
from google.cloud import aiplatform_v1beta1
from dotenv import load_dotenv

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

def check_model(model_name: str, location: str):
    logger.info(f"Checking '{model_name}' in '{location}'...")
    try:
        api_endpoint = f"{location}-aiplatform.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}
        client = aiplatform_v1beta1.ModelGardenServiceClient(client_options=client_options)
        
        resource_name = f"publishers/google/models/{model_name}"
        logger.info(f" Resource Name: {resource_name}")
        
        client.get_publisher_model(name=resource_name)
        logger.info(f"FOUND: {model_name} is available in {location}")
        return True
    except Exception as e:
        logger.error(f"NOT FOUND: {model_name} in {location}")
        logger.error(f"   Error details: {e}")
        return False

def list_us_central_models():
    logger.info("Fetching Master Catalog from us-central1...")
    try:
        client = aiplatform_v1beta1.ModelGardenServiceClient(
            client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
        )
        response = client.list_publisher_models(parent="publishers/google")
        found = []
        for m in response.publisher_models:
            mid = m.name.split('/')[-1]
            if 'preview' in mid.lower(): # Focus on previews
                found.append(mid)
        
        logger.info(f"Found {len(found)} preview models in global catalog.")
        for f in sorted(found):
            msg = f" - {f}"
            if "gemini-3" in f: 
                 msg += " <--- TARGET"
            logger.info(msg)
            
        return found
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []

if __name__ == "__main__":
    target_model = "gemini-3-pro-preview"
    target_loc = os.getenv("VERTEX_LOCATION", "europe-north1")
    
    print("="*60)
    print(" MODEL AVAILABILITY PROBE")
    print(f" Target Location: {target_loc}")
    print("="*60)
    
    # 1. Listing
    preview_models = list_us_central_models()
    
    # 2. Probing
    print("-" * 60)
    res = check_model(target_model, target_loc)
    
    if not res:
        print("\nPossible Issue: The model exists globally but not in the target region.")
        print("Recommendation: Switch VERTEX_LOCATION to 'us-central1' or use a supported model.")
