import sys
import os
import requests

# Assuming backend is running on localhost:8000
BACKEND_URL = "http://localhost:8000"

def test_schemas():
    try:
        print(f"Fetching schemas from {BACKEND_URL}/config/schemas...")
        res = requests.get(f"{BACKEND_URL}/config/schemas")
        
        if res.status_code == 200:
            data = res.json()
            print(f"Success! Found {len(data)} schemas.")
            print("Schemas found:", list(data.keys()))
            
            if "TaintedData" in data:
                print("\nExample for TaintedData:")
                print(data["TaintedData"].get("example"))
            else:
                print("WARNING: TaintedData schema not found!")
        else:
            print(f"Failed: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_schemas()
