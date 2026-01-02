
import os
import logging
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pure_vertex_discovery():
    load_dotenv()
    
    vertex_location = os.getenv("VERTEX_LOCATION")
    vertex_project = os.getenv("VERTEX_PROJECT_ID")
    
    logger.info(f"Target Project: {vertex_project}")
    logger.info(f"Target Region: {vertex_location}")
    
    if not vertex_location or not vertex_project:
        logger.error("Missing VERTEX_LOCATION or VERTEX_PROJECT_ID env var.")
        return

    try:
        logger.info("Initializing Vertex AI Client (aiplatform v1)...")
        # We assume Application Default Credentials (ADC) are set, or gcloud auth is active.
        service = build('aiplatform', 'v1', cache_discovery=False)
        
        parent = f"projects/{vertex_project}/locations/{vertex_location}"
        
        # This is the call used in Phase 2
        # We query the 'google' publisher specifically to limit noise
        logger.info(f"Querying: {parent}/publishers/google/models")
        
        request = service.projects().locations().publishers().models().list(
            parent=f"{parent}/publishers/google"
        )
        response = request.execute()
        
        models_found = []
        if 'models' in response:
            for m in response['models']:
                # m['name'] -> projects/.../publishers/google/models/gemini-pro
                # m['versionId'] -> might be available
                model_id = m['name'].split('/')[-1]
                models_found.append(model_id)
                logger.info(f"Found Model Raw: {model_id} (Resource: {m['name']})")
        
        # Filter for Gemini
        gemini_models = [m for m in models_found if 'gemini' in m.lower()]
        
        logger.info("-" * 30)
        logger.info(f"Total Models Found: {len(models_found)}")
        logger.info(f"Gemini Models Found: {len(gemini_models)}")
        logger.info(f"Gemini List: {gemini_models}")
        
        if len(gemini_models) > 0:
            logger.info("VERDICT: SUCCESS. Pure Vertex discovery works independently.")
        else:
            logger.warning("VERDICT: FAILURE/UNCERTAIN. No Gemini models returned. Phase 1 might be needed.")

    except Exception as e:
        logger.error(f"Vertex API Call Failed: {e}", exc_info=True)

if __name__ == "__main__":
    test_pure_vertex_discovery()
