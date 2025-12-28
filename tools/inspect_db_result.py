import json
import sys

DB_PATH = "c:/Users/risto/OneDrive/quorum/backend/database/db_mock.json"
EXEC_ID = "3d7f5293-aa0c-4209-9511-189a3782d621"

try:
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    executions = data.get("_default", {})
    
    print(f"Total records in _default: {len(executions)}")
    ids = []
    for key, val in executions.items():
        eid = val.get("id")
        ids.append(eid)
        if eid == EXEC_ID:
            target_exec = val
            
    print(f"Found IDs: {ids}")
    
    if target_exec:
        result = target_exec.get("result", {})
        raw_steps = result.get("Raw_Steps", {})
        print(f"Execution {EXEC_ID} found.")
        print(f"Raw_Steps keys: {list(raw_steps.keys())}")
        if "step_judge_cognitive" in raw_steps:
            print("step_judge_cognitive IS Present.")
            print(json.dumps(raw_steps["step_judge_cognitive"], indent=2))
        else:
            print("step_judge_cognitive is MISSING.")
    else:
        print(f"Execution {EXEC_ID} NOT found in db_mock.json.")
        
except Exception as e:
    print(f"Error: {e}")
