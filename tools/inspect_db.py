import json
import os

DB_PATH = r"c:\Users\risto\OneDrive\quorum\backend\database\db_mock.json"

try:
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    executions = data.get('executions', {})
    print(f"Total executions: {len(executions)}")
    
    # Get latest
    keys = list(executions.keys())
    if not keys:
        print("No executions found.")
        exit()
        
    last_id = keys[-1]
    last_exec = executions[last_id]
    
    print(f"Latest Execution: {last_id}")
    res = last_exec.get('result', {})
    
    print("Keys in 'result':")
    print(list(res.keys()))
    
    raw = res.get('Raw_Steps', {})
    print("Keys in 'result.Raw_Steps':")
    print(list(raw.keys()))

    if 'step_judge_cognitive' in raw:
        print("✅ step_judge_cognitive FOUND in 'Raw_Steps'")
    else:
        print("❌ step_judge_cognitive NOT FOUND in 'Raw_Steps'")
        
except Exception as e:
    print(f"Error: {e}")
