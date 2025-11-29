import json
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from src.api.server import app

def generate_openapi():
    openapi_schema = app.openapi()
    with open("docs/openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print("openapi.json generated in docs/")

if __name__ == "__main__":
    generate_openapi()
