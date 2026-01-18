
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
    
    iter_items = []
    if isinstance(results, list):
        iter_items = results
    elif isinstance(results, dict):
        iter_items = results.values()
        
    if iter_items:
        first_item = list(iter_items)[0]
        print(f"First item type: {type(first_item)}")
        print(f"First item RAW (first 500 chars): {str(first_item)[:500]}")

except Exception as e:
    print(f"Error: {e}")
