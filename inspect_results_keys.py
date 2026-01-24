
import json
import sys

db_path = r"c:\src\quorum\data\db.json"
exec_key = "14"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    execution = data.get("executions", {}).get(exec_key)
    if not execution:
        print(f"Execution Key {exec_key} not found.")
        sys.exit(1)
        
    results = execution.get("results", {})
    print(f"Results Keys: {list(results.keys())}")
    
    # Check XAI
    xai = results.get("step_xai", {})
    print(f"XAI Status: {xai.get('status')}")

except Exception as e:
    print(f"Error: {e}")
