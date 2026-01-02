import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
ROOT_TOKEN = "mock-token:root_master"

print("--- DEBUGGING IAM ENDPOINTS ---")

try:
    print(f"1. Testing GET /organizations/ with ROOT_TOKEN")
    resp = client.get("/organizations/", headers={"Authorization": f"Bearer {ROOT_TOKEN}"})
    print(f"Status: {resp.status_code}")
    try:
        print(f"Response: {resp.json()}")
    except:
        print(f"Response Text: {resp.text}")
    
except Exception as e:
    print(f"EXCEPTION: {e}")

print("--- END DEBUG ---")
