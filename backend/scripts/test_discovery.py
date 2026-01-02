from backend.llm.handler import LLMHandler
from backend.database.wrapper import get_db_client
import sys
import os

# Set dummy env for test if not present
if not os.getenv("VERTEX_PROJECT_ID"):
    print("WARNING: VERTEX_PROJECT_ID not set. This test might fail if no default creds.")

# Set mock location to test validation logic (unless overridden)
target_loc = "europe-north1"
if len(sys.argv) > 1:
    target_loc = sys.argv[1]

print(f"Testing Discovery for Location: {target_loc}")

# Initialize
db = get_db_client() # Needs working DB path or will create new
handler = LLMHandler(db)

# Call Fetch (Using filters to skip OpenAI or Mock if desired, but testing full flow)
# We pass location explicitly to force validation path
try:
    models = handler.fetch_all_available_models(providers=['google'], location=target_loc)

    print("\n--- RESULTS ---")
    if "google" in models:
        print(f"Google Models Found ({len(models['google'])}):")
        for m in models['google']:
            print(f" - {m}")
    else:
        print("No 'google' key in results.")
        
    if "google_error" in models:
        print(f"ERROR: {models['google_error']}")
        
    if "google_warning" in models:
        print(f"WARNING: {models['google_warning']}")

except Exception as e:
    print(f"CRITICAL FAIL: {e}")
