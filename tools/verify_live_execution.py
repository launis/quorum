
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"
WORKFLOW_ID = "wf-courtroom-2-0-dual-matrix-6685039d"
TOKEN = "mock-token:root_master"

def run_verification():
    print(f"Targeting: {BASE_URL}")
    print(f"Workflow: {WORKFLOW_ID}")
    
    # 1. Trigger Execution
    print("Triggering execution...")
    try:
        resp = requests.post(
            f"{BASE_URL}/executions",
            data={
                "workflow_id": WORKFLOW_ID,
                "inputs": json.dumps({
                    "history_text": "Q: What is the capital of Finland? A: Helsinki.",
                    "product_text": "The answer is Helsinki.",
                    "reflection_text": "I answered correctly."
                })
            },
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        if resp.status_code != 200:
            print(f"Failed to trigger: {resp.status_code} - {resp.text}")
            return
            
        exec_id = resp.json().get('execution_id')
        print(f"Started Execution ID: {exec_id}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 2. Poll for Completion
    print("Polling for completion...")
    status = "pending"
    while status not in ['completed', 'failed', 'rejected']:
        time.sleep(2)
        try:
            r = requests.get(
                f"{BASE_URL}/executions/{exec_id}", 
                headers={"Authorization": f"Bearer {TOKEN}"}
            )
            data = r.json()
            status = data.get('status')
            step = data.get('current_step_name')
            print(f"Status: {status} (Step: {step})")
        except Exception as e:
            print(f"Polling error: {e}")
            break
            
    # 3. Inspect Result
    if status == 'completed':
        print("\n--- EXECUTION COMPLETED ---")
        result = data.get('result', {})
        
        # Check comparison_data
        comp_data = result.get('comparison_data')
        if comp_data:
            print("SUCCESS: comparison_data found in API response!")
            print(json.dumps(comp_data, indent=2))
        elif 'step_reporter' in result and 'comparison_data' in result['step_reporter']:
             # Check nested if not flattened
             print("SUCCESS: comparison_data found in step_reporter!")
             print(json.dumps(result['step_reporter']['comparison_data'], indent=2))
        else:
            print("FAILURE: comparison_data NOT found in result.")
            print("Result keys:", result.keys())
            
        # Check step_judge
        print("\n--- Audit Results ---")
        if 'audit_results' in result:
             print(f"Audit Results keys: {result['audit_results'].keys()}")
        elif '_meta' in result:
             print(f"Meta: {result['_meta']}")

    else:
        print(f"\nExecution finished with non-success status: {status}")
        print(f"Error: {data.get('error')}")

if __name__ == "__main__":
    run_verification()
