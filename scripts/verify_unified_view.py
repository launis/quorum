import requests
import json
import sys

BACKEND_URL = "http://localhost:8000"

def test_unified_view():
    print("Fetching Unified Master View...")
    try:
        res = requests.get(f"{BACKEND_URL}/config/unified-prompts")
        if res.status_code != 200:
            print(f"FAILED: Status code {res.status_code}")
            print(res.text)
            sys.exit(1)
        
        content = res.json().get("content", "")
        print(f"Received content length: {len(content)}")
        
        # Check for expected schemas
        expected_schemas = [
            "TaintedData",
            "TodistusKartta",
            "ArgumentaatioAnalyysi",
            "LogiikkaAuditointi",
            "KausaalinenAuditointi",
            "PerformatiivisuusAuditointi",
            "EtiikkaJaFakta",
            "TuomioJaPisteet",
            "XAIReport"
        ]
        
        missing = []
        for schema in expected_schemas:
            if schema not in content:
                print(f"WARNING: Schema name '{schema}' not found in content text (might be expanded).")
            
            # Check for expanded content (look for some keys or structure)
            # This is harder to check generally, but we can check if the placeholder is GONE
            placeholder = f"[Ks. schemas.py / {schema}]"
            if placeholder in content:
                print(f"FAILED: Placeholder '{placeholder}' was NOT expanded.")
                missing.append(schema)
            else:
                print(f"SUCCESS: Placeholder for '{schema}' appears to be expanded.")
                
        if missing:
            print(f"Failed schemas: {missing}")
            sys.exit(1)
            
        print("All schema placeholders expanded successfully.")
        
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_unified_view()
