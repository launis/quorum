import sys
import os
import json

# Add the current directory to sys.path so we can import the backend module
sys.path.append(os.getcwd())

# FORCE MOCK MODE to bypass credential checks in Settings
os.environ["USE_MOCK_LLM"] = "True"
os.environ["USE_MOCK_DB"] = "True"

try:
    from backend.main import app
except Exception as e:
    import traceback
    print(f"CRITICAL ERROR importing backend.main: {e}")
    traceback.print_exc()
    sys.exit(1)

def generate_openapi():
    """
    Generates the OpenAPI JSON schema and saves it to docs/openapi.json.
    """
    print("Generating OpenAPI spec...")
    openapi_schema = app.openapi()
    
    output_path = os.path.join("docs", "openapi.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
        
    print(f"Successfully saved OpenAPI spec to {output_path}")

if __name__ == "__main__":
    generate_openapi()
