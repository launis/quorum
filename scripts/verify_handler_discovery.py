
import sys
import os
import asyncio
from dotenv import load_dotenv

# Ensure backend can be imported
sys.path.append(os.getcwd())
load_dotenv(override=True)

from backend.llm.handler import LLMHandler

# Mock DB client since we only need discovery
class MockDB:
    def table(self, name):
        return self
    def search(self, query):
        return []

def test_handler_discovery():
    print("Testing LLMHandler.fetch_all_available_models()...")
    handler = LLMHandler(db_client=MockDB())
    
    try:
        models = handler.fetch_all_available_models(providers=["google"])
        print(f"✅ Handler returned: {models.keys()}")
        
        google_models = models.get("google", [])
        if google_models:
             print(f"✅ Found {len(google_models)} Google models.")
             print(f"Sample: {google_models[:5]}...")
             
             # Check for gemini
             geminis = [m for m in google_models if "gemini" in m.lower()]
             print(f"Gemini count: {len(geminis)}")
        else:
            print("❌ No Google models returned.")
            if "google_error" in models:
                print(f"Error: {models['google_error']}")

    except Exception as e:
        # Check if it's our structured exception
        if hasattr(e, "message") and hasattr(e, "details"):
             print(f"✅ Handler raised expected AppException: {e.message}")
             print(f"   Details: {e.details}")
        else:
             print(f"❌ Handler crashed with unexpected error: {e.__class__.__name__}: {e}")

if __name__ == "__main__":
    test_handler_discovery()
