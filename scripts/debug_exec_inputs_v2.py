
import json
import sys

db_path = "c:/src/quorum/data/db.json"
exec_id = "ff5f84fb-ed55-4648-9c63-fbfa405dd96e"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_exec = None
    
    if "executions" in data:
        executions = data["executions"]
        if isinstance(executions, dict):
             for key, record in executions.items():
                if record.get("id") == exec_id or record.get("execution_id") == exec_id:
                    target_exec = record
                    break
    elif "_default" in data: 
        for key, record in data["_default"].items():
             if record.get("id") == exec_id or record.get("execution_id") == exec_id:
                target_exec = record
                break
    
    if not target_exec:
        print(f"Execution {exec_id} not found.")
        sys.exit(1)
        
    print("\n--- GLOBAL SETTINGS / INPUTS ---")
    inputs = target_exec.get("inputs", {})
    if isinstance(inputs, dict):
         print(json.dumps(inputs, indent=2))
    else:
         print(str(inputs))
    
    # Check if history_text is present
    if isinstance(inputs, dict):
        print(f"\nhistory_text present: {'history_text' in inputs}")
    

except Exception as e:
    print(f"Error: {e}")
