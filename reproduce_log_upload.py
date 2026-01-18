
import requests
import jwt
import time
import os
from datetime import datetime, timezone, timedelta

# Configuration
API_URL = "http://localhost:8000"
JWT_SECRET = "cognitive-quorum-internal-secret-change-me"  # Hardcoded default from auth.py
WORKFLOW_ID = "sequential_audit_chain" # Correct ID from seed/db
USER_ID = "root_master" # Valid user from seed_data.json
ORG_ID = "system"

def generate_token():
    """Generates a valid JWT token for local testing."""
    payload = {
        "sub": USER_ID,
        "uid": USER_ID,
        "email": "root@cognitive-quorum.local",
        "org_id": ORG_ID,
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def reproduction_log_upload():
    print(f"--- Reproducing .log file upload for workflow: {WORKFLOW_ID} ---")
    
    # 1. Create a dummy log file
    log_content = """[10:00] User: Here is a log file.
[10:01] AI: I see. It has timestamps.
[10:02] User: Can you parse it?
"""
    with open("test_chat.log", "w", encoding="utf-8") as f:
        f.write(log_content)
        
    print(f"Created test_chat.log (Length: {len(log_content)})")

    # 2. Prepare headers with Auth
    token = generate_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Prepare Multipart Payload
    # Note: 'json_payload' field is used for metadata
    # Files are attached with specific keys.
    
    files = {
        'history_text': ('test_chat.log', open('test_chat.log', 'rb'), 'text/plain'), # Explicit mime for now, but parser should rely on ext
    }
    
    data = {
        "workflowId": WORKFLOW_ID, 
        # We can also populate 'json_payload' if we wanted mixed inputs, but direct files are supported
    }

    try:
        print(f"Sending POST /executions to {API_URL}...")
        response = requests.post(f"{API_URL}/executions", headers=headers, files=files, data=data)
        
        print(f"Response Status: {response.status_code}")
        if response.status_code == 201:
            print("Success! Execution created.")
            print(response.json())
        else:
            print("Failed.")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if os.path.exists("test_chat.log"):
            os.remove("test_chat.log")

if __name__ == "__main__":
    reproduction_log_upload()
