import requests
import time
import os
import subprocess
import sys
import threading
import uvicorn
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.server import app

# We can use TestClient for synchronous testing without spinning up a real server
client = TestClient(app)

def test_health_check():
    print("\n--- Testing Health Check ---")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_workflow_execution():
    print("\n--- Testing Workflow Execution (Mock) ---")
    
    # 1. Create dummy files
    files = {
        "history_file": ("history.txt", "User: Hello\nAI: Hi", "text/plain"),
        "product_file": ("product.txt", "My Essay", "text/plain"),
        "reflection_file": ("reflection.txt", "I did well", "text/plain")
    }
    
    # 2. Start Job
    # We need a valid workflow ID. Let's fetch one first or use a known one.
    # For testing, we might need to mock the DB if we don't have one running.
    # But let's try to hit the endpoint.
    
    # Note: This test assumes the DB is accessible (TinyDB locally or Firestore if configured)
    # If using TinyDB, ensure seed data is present.
    
    try:
        # Get workflows
        res = client.get("/db/workflows")
        if res.status_code == 200 and len(res.json()) > 0:
            workflow_id = res.json()[0]['id']
            print(f"Using Workflow ID: {workflow_id}")
            
            response = client.post(
                "/orchestrator/run",
                params={"workflow_id": workflow_id},
                files=files
            )
            
            print(f"Start Job Status: {response.status_code}")
            if response.status_code == 200:
                job_id = response.json()['job_id']
                print(f"Job ID: {job_id}")
                
                # 3. Poll Status
                for _ in range(10):
                    status_res = client.get(f"/orchestrator/status/{job_id}")
                    status = status_res.json()['status']
                    print(f"Job Status: {status}")
                    if status in ["COMPLETED", "FAILED"]:
                        break
                    time.sleep(1)
            else:
                print(f"Error: {response.text}")
        else:
            print("No workflows found or DB error.")
            
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_health_check()
    test_workflow_execution()
