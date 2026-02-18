import vertexai
from vertexai.generative_models import GenerativeModel, Tool
import os
import sys
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("VERTEX_LOCATION", "europe-north1")

# Use modern Gemini 2.0 model
MODEL_ID = "gemini-2.5-pro" 

def test_grounding():
    print(f"[TEST] Testing Vertex AI Grounding (Project: {PROJECT_ID}, Model: {MODEL_ID})...", flush=True)
    
    if not PROJECT_ID:
        print("[ERROR] GOOGLE_CLOUD_PROJECT environment variable is missing.", flush=True)
        return

    try:
        # 2. Initialization
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # 3. Define Tool (FIX)
        # Using Tool.from_dict to enforce 'google_search' structure
        print("[INFO] Creating tool using 'google_search' field...", flush=True)
        
        google_search_tool = Tool.from_dict({
            "google_search": {} 
        })
        
        # 4. Load Model
        model = GenerativeModel(MODEL_ID) 
        
        # 5. Ask Question
        prompt = "Who won the latest ice hockey world championship and with what score?"
        print(f"\nQuestion: '{prompt}'", flush=True)
        print("Fetching answer via Google...\n", flush=True)

        response = model.generate_content(
            prompt,
            tools=[google_search_tool],
            generation_config={
                "temperature": 0.0
            }
        )
        
        # 6. Print Response
        print("--- ANSWER ---", flush=True)
        try:
            print(response.text, flush=True)
        except ValueError:
            print("(Answer blocked for safety or was empty)", flush=True)
        
        # 7. Print Sources
        print("\n--- SOURCES (Grounding Metadata) ---", flush=True)
        has_metadata = False
        if response.candidates:
             cand = response.candidates[0]
             if hasattr(cand, "grounding_metadata") and cand.grounding_metadata:
                metadata = cand.grounding_metadata
                has_metadata = True
                
                if metadata.search_entry_point:
                    print(f"Search executed: {metadata.search_entry_point.rendered_content}", flush=True)
                
                found_sources = False
                if metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        if chunk.web:
                            print(f"[SOURCE] {chunk.web.title} ({chunk.web.uri})", flush=True)
                            found_sources = True
                
                if not found_sources:
                    print("[WARN] No direct web sources in response.", flush=True)
                else:
                    print("\n[PASS] TEST PASSED: Grounding operational!", flush=True)
        
        if not has_metadata:
             print("[WARN] No metadata available.", flush=True)

    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grounding()