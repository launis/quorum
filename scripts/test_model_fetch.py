import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_fetch():
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"API Key Present: {bool(api_key)}")
    
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment.")
        return

    try:
        genai.configure(api_key=api_key)
        print("Attempting to list models...")
        
        found = []
        for m in genai.list_models():
            print(f"- {m.name} (Methods: {m.supported_generation_methods})")
            if 'generateContent' in m.supported_generation_methods:
                found.append(m.name)
                
        print(f"\nTotal compatible models found: {len(found)}")
        print("Compatible Models:", found)
        
    except Exception as e:
        print(f"ERROR: Failed to list models: {e}")

if __name__ == "__main__":
    test_fetch()
