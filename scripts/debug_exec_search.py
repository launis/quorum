
import json
import sys

db_path = "c:/src/quorum/data/db.json"
exec_id = "ff5f84fb-ed55-4648-9c63-fbfa405dd96e"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_exec = None
    
    # Locate execution
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
        
    s_dump = json.dumps(target_exec)
    idx = s_dump.find("step_guard")
    
    if idx != -1:
        print(f"Found 'step_guard' at index {idx}")
        start = max(0, idx - 200)
        end = min(len(s_dump), idx + 1000) # Print enough to see the structure
        print(f"Context:\n{s_dump[start:end]}")
        
        # Try to find if it is a key
        # Look for "step_id": or "name": around it
    else:
        print("'step_guard' not found in execution record string.")

except Exception as e:
    print(f"Error: {e}")
