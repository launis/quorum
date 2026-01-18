
import json
import sys

db_path = "c:/src/quorum/data/db.json"
exec_id = "ff5f84fb-ed55-4648-9c63-fbfa405dd96e"
search_term = "12345"

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
    history_text = results.get("history_text", "")
    
    print(f"Searching for '{search_term}' in history_text ({len(history_text)} chars)...")
    
    if search_term in history_text:
        print(f"FOUND: '{search_term}' is present in the input.")
        idx = history_text.find(search_term)
        start = max(0, idx - 50)
        end = min(len(history_text), idx + 50)
        print(f"Context: ...{history_text[start:end]}...")
    else:
        print(f"NOT FOUND: '{search_term}' is NOT in the input.")

except Exception as e:
    print(f"Error: {e}")
