
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
        
    results = target_exec.get("results", {})
    if isinstance(results, dict):
        print(f"Results keys: {list(results.keys())}")
        print(f"history_text in results: {'history_text' in results}")
    else:
        print(f"Results type: {type(results)}")

except Exception as e:
    print(f"Error: {e}")
