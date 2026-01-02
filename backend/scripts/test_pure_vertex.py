import os
import logging
import google.auth
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pure_vertex_discovery():
    load_dotenv()
    
    vertex_location = "us-central1" 
    vertex_project = os.getenv("VERTEX_PROJECT_ID")
    
    if not vertex_project:
        try:
            _, project_id = google.auth.default()
            vertex_project = project_id
            logger.info(f"Resolved Project ID from ADC: {vertex_project}")
        except Exception as e:
            logger.error(f"Could not resolve Project ID from ADC: {e}")

    if not vertex_location or not vertex_project:
        logger.error("Missing VERTEX_PROJECT_ID and could not resolve from ADC.")
        return

    try:
        logger.info(f"Target: {vertex_project} @ {vertex_location}")
        logger.info("Initializing Vertex AI Client (aiplatform v1beta1)...")
        
        service = build('aiplatform', 'v1beta1', cache_discovery=False)
        
        parent = f"projects/{vertex_project}/locations/{vertex_location}"
        
        # Inspection
        locs = service.projects().locations()
        # logger.info(f"Locations methods: {dir(locs)}")
        
        # Try publishers
        pubs = locs.publishers()
        # logger.info(f"Publishers methods: {dir(pubs)}")
        
        logger.info(f"Querying: {parent}/publishers/google/models")
        
        # Note: In some versions, the collection might be 'models' 
        # but check if 'models' is method on 'pubs'
        
        model_request = pubs.models().list(
            parent=f"{parent}/publishers/google"
        )
        response = model_request.execute()
        
        models_found = []
        if 'models' in response:
            for m in response['models']:
                model_id = m['name'].split('/')[-1]
                models_found.append(model_id)
        
        gemini_models = [m for m in models_found if 'gemini' in m.lower()]
        
        logger.info("-" * 30)
        logger.info(f"Total Models Found: {len(models_found)}")
        logger.info(f"Gemini Models Found: {len(gemini_models)}")
        # Print first 5 Gemini models
        logger.info(f"Gemini Examples: {gemini_models[:5]} ...")
        
        if len(gemini_models) > 0:
            logger.info("VERDICT: SUCCESS. US-Central1 discovery works.")
        else:
            logger.warning("VERDICT: FAILURE. Connected but no Gemini models found.")

    except Exception as e:
        logger.error(f"Vertex API Call Failed: {e}", exc_info=True)

if __name__ == "__main__":
    test_pure_vertex_discovery()
