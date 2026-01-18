
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
    
    results = target_exec.get("results", {})
    
    iter_items = []
    if isinstance(results, list):
        iter_items = results
    elif isinstance(results, dict):
        iter_items = results.values()
        
    if iter_items:
        first_item = list(iter_items)[0]
        if isinstance(first_item, str):
            try:
                first_item = json.loads(first_item)
            except:
                pass
        
        print(f"First item type: {type(first_item)}")
        if isinstance(first_item, dict):
            print(f"First item keys: {list(first_item.keys())}")
            # If it has a 'data' key, print its keys too
            if 'data' in first_item:
                 print(f"First item['data'] keys: {list(first_item['data'].keys()) if isinstance(first_item['data'], dict) else type(first_item['data'])}")

except Exception as e:
    print(f"Error: {e}")
