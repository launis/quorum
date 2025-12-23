import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print(f"Using API at {BASE_URL}")

    # 1. Start Execution
    payload = {
        "workflow_id": "sequential_audit_chain", 
        "inputs": {
            "history_text": "Testauksen historia",
            "product_text": "Testauksen lopputuote", 
            "reflection_text": "Testauksen reflektio"
        }
    }
    
    try:
        print("Sending POST /executions...")
        resp = requests.post(f"{BASE_URL}/executions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        exec_id = data['execution_id']
        print(f"Execution started: {exec_id}")
    except Exception as e:
        print(f"Failed to start execution: {e}")
        sys.exit(1)

    # 2. Poll for completion
    while True:
        time.sleep(2)
        try:
            r = requests.get(f"{BASE_URL}/executions/{exec_id}")
            r.raise_for_status()
            current = r.json()
            status = current['status']
            print(f"Status: {status}")
            
            if status in ['completed', 'failed', 'rejected']:
                break
        except Exception as e:
            print(f"Polling failed: {e}")
            break

    # 3. Verify Result
    if status == 'completed':
        result = current.get('result', {})
        keys = list(result.keys())
        print(f"Final Result Keys: {keys}")
        
        if 'Scores' in result:
             print("SUCCESS: 'Scores' object found (V2 Structure confirmed).")
             print(f"Scores Content: {result['Scores']}")
        
        missing = [k for k in ['step_judge', 'step_guard', 'step_analyst'] if k not in result]
        
        if not missing:
            print("SUCCESS: All critical steps found in result.")
            print(f"Judge Score: {result['step_judge'].get('pisteet', 'N/A')}")
        else:
            print(f"FAILURE: Missing keys in result: {missing}")
            sys.exit(1)
    else:
        print(f"Execution finished with unexpected status: {status}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
