import requests
import json

def run():
    # 1. Read existing raw_inputs from db_v2.json
    db_path = 'c:/src/quorum/data/db_v2.json'
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    execs = [e for e in db.get('executions', {}).values() if e.get('id') == 'exe_a678edba4265486ebc273b7a0745d362']
    if not execs:
        print("Original execution not found!")
        return
        
    raw_inputs = execs[0].get('raw_inputs', {})

    # 2. Build Payload
    url = "http://127.0.0.1:8000/api/v2/execution/executions"
    payload = {
        "workflow_id": "wf_d653170e174847559e08af42b938d826",
        "target_locale": "fi",
        "raw_inputs": raw_inputs
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer mock-token:usr_43ec77a438104814bd937f28853d569c"
    }
    
    # 3. Trigger
    print("Triggering clone execution...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code in (200, 201, 202):
            data = response.json()
            print("Execution created successfully!")
            print(f"New Execution ID: {data.get('id')}")
        else:
            print("Failed Response:", response.text)
    except Exception as e:
        print("Error sending request:", e)

if __name__ == "__main__":
    run()
