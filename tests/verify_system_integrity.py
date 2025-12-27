import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_connection():
    try:
        r = requests.get(f"{BASE_URL}/docs")
        if r.status_code == 200:
            log("Backend connection successful.", "SUCCESS")
            return True
    except:
        log("Cannot connect to backend. Is it running?", "ERROR")
        return False

def test_validation_logic():
    log("Testing Data Flow Validation Logic...")
    
    # 1. Valid Sequence (Guard -> Analyst -> Judge)
    # Note: Using standard IDs from seed
    valid_seq = ["step_guard", "step_analyst", "step_judge"]
    payload_valid = {"id": "test_1", "name": "Valid Test", "sequence": valid_seq, "description": "test"}
    
    try:
        r = requests.post(f"{BASE_URL}/config/validate-flow", json=payload_valid)
        res = r.json()
        if res.get('valid') == True:
            log("Valid sequence passed validation.", "SUCCESS")
        else:
            log(f"Valid sequence FAILED validation: {res.get('errors')}", "FAIL")
            
        # 2. Invalid Sequence (Judge Only - missing Guard output)
        invalid_seq = ["step_judge"]
        payload_invalid = {"id": "test_2", "name": "Invalid Test", "sequence": invalid_seq, "description": "test"}
        
        r2 = requests.post(f"{BASE_URL}/config/validate-flow", json=payload_invalid)
        res2 = r2.json()
        if res2.get('valid') == False and any("MISSING INPUTS" in e for e in res2.get('errors', [])):
             log("Invalid sequence correctly rejected (Missing Inputs detected).", "SUCCESS")
        else:
             log(f"Invalid sequence was NOT rejected correctly: {res2}", "FAIL")

    except Exception as e:
        log(f"Validation test failed with exception: {e}", "ERROR")

def test_execution_run():
    log("Testing Real Workflow Execution (Mock)...")
    
    # 1. Get Workflow ID (Default)
    try:
        wfs = requests.get(f"{BASE_URL}/db/workflows").json()
        wf_id = wfs[0]['id']
        log(f"Using Workflow: {wf_id}")
    except:
        log("Failed to fetch workflows", "ERROR")
        return

    # 2. Start Execution
    payload = {
        "workflow_id": wf_id,
        "inputs": json.dumps({
             "history_text": "This is a test history.",
             "product_text": "This is a test product text.",
             "reflection_text": "Reflection."
        })
    }
    
    start_res = requests.post(f"{BASE_URL}/executions", data=payload)
    if start_res.status_code != 200:
        log(f"Start failed: {start_res.text}", "ERROR")
        return
        
    exec_id = start_res.json()['execution_id']
    log(f"Execution started: {exec_id}")
    
    # 3. Poll Status
    for i in range(60): # Wait up to 60s
        time.sleep(1)
        stat = requests.get(f"{BASE_URL}/executions/{exec_id}").json()
        status = stat['status']
        stage = stat.get('stage', 'Unknown')
        percent = stat.get('percent', 0)
        log(f"Status: {status} | Stage: {stage} | Progress: {percent}%")
        
        if status == 'completed':
            log("Execution COMPLETED successfully!", "SUCCESS")
            # Verify result has scores
            res = stat.get('result', {})
            
            # V2 Structure Support: Check Raw_Steps or Report
            if "step_judge" in res: # Legacy or Hoisted
                 log("Result contains Judge output (Top Level).", "SUCCESS")
            elif "Raw_Steps" in res and "step_judge" in res["Raw_Steps"]:
                 log("Result contains Judge output (in Raw_Steps).", "SUCCESS")
            elif "Report" in res and "scores" in res["Report"]:
                 log("Result contains Judge output (Report Scores).", "SUCCESS")
            else:
                log(f"Result missing Judge output. Keys: {list(res.keys())}", "WARNING")
            return
            
        if status == 'failed':
            log(f"Execution FAILED: {stat.get('error')}", "ERROR")
            return
            
    log("Execution timed out or stuck.", "WARNING")

if __name__ == "__main__":
    if test_connection():
        test_validation_logic()
        test_execution_run()
    else:
        sys.exit(1)
