import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests

try:
    print("Hitting API...")
    response = requests.get("http://localhost:8000/db/workflows")
    print(f"Status: {response.status_code}")
    print(response.text)

except Exception as e:
    print(f"Error: {e}")
