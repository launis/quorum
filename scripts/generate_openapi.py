import sys
import os
import json

# Add the current directory to sys.path so we can import the backend module
sys.path.append(os.getcwd())

try:
    from backend.main import app
except ImportError as e:
    print(f"Error importing backend.main: {e}")
    sys.exit(1)

def generate_openapi():
    """
    Generates the OpenAPI JSON schema and saves it to docs/openapi.json.
    """
    print("Generating OpenAPI spec...")
    openapi_schema = app.openapi()
    
    output_path = os.path.join("docs", "openapi.json")
    
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
        
    print(f"Successfully saved OpenAPI spec to {output_path}")

if __name__ == "__main__":
    generate_openapi()
