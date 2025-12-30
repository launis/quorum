import requests
import sys

BACKEND_URL = "http://localhost:8000"

def test_unified_prompts():
    try:
        print(f"Fetching unified prompts from {BACKEND_URL}/config/unified-prompts...")
        res = requests.get(f"{BACKEND_URL}/config/unified-prompts")
        
        if res.status_code == 200:
            data = res.json()
            content = data.get("content", "")
            print(f"Success! Received {len(content)} characters.")
            
            # Check for key markers
            if "# KOGNITIIVINEN KVOORUM" in content:
                print(" - Header found.")
            else:
                print(" - WARNING: Header NOT found.")
                
            if "### PROMPT_GUARD" in content:
                print(" - PROMPT_GUARD found.")
            else:
                print(" - WARNING: PROMPT_GUARD NOT found.")
                
            # Check for schema expansion (look for a JSON block)
            if "```json" in content and "TaintedData" in content: # TaintedData is likely in PROMPT_GUARD
                print(" - Schema expansion appears to be working (found JSON block).")
            else:
                print(" - WARNING: Schema expansion might not be working.")
                
        else:
            print(f"Failed: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_unified_prompts()
