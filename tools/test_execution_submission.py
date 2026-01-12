import requests
import json

# URL of the local backend
URL = "http://127.0.0.1:8000/executions"
# Workflow ID for a Courtroom (Audit) workflow known to exist (e.g., from seed data)
WORKFLOW_ID = "sequential_audit_chain" 

def test_submission():
    print(f"Testing submission to {URL}...")

    # Simulating Flutter: 'inputs' field is a JSON string
    # Case 1: All inputs as JSON text
    inputs_dict = {
        "history_text": "Test History",
        "product_text": "Test Product",
        "reflection_text": "Test Reflection"
    }
    
    # Prepare Pydantic model payload
    execution_req = {
        "project_id": WORKFLOW_ID,
        "settings": inputs_dict,
        "description": "Test execution via script"
    }

    # Multipart/form-data request
    try:
        headers = {
            "Authorization": "Bearer mock-token:root_master"
        }
        
        # In New Schema:
        # 1. JSON Payload is sent as 'json_payload' field (plain string, no content-type)
        #    Note: Passing (None, str) makes requests send it as a form field.
        # 2. Files are sent as normal files
        files = {
            'json_payload': (None, json.dumps(execution_req)),
            'history_text': ('history.txt', b'Test History', 'text/plain'),
            'product_text': ('product.txt', b'Test Product', 'text/plain'),
            'reflection_text': ('reflection.txt', b'Test Reflection', 'text/plain'),
        }
        
        response = requests.post(URL, files=files, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
             print(f"Response Body: {response.text}")
        
        try:
            data = response.json()
            if 'detail' in data:
                print(f"Response Detail: {data.get('detail')}")
        except:
            pass
        
        if response.status_code == 200:
            print("SUCCESS: Backend accepted JSON inputs.")
        else:
            print("FAILURE: Backend rejected inputs.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_submission()
