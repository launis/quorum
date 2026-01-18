
import json
import re
import sys

db_path = "c:/src/quorum/data/db.json"
exec_id = "ff5f84fb-ed55-4648-9c63-fbfa405dd96e"
search_term = "asiakasnumero"

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
    
    print(f"Searching for '{search_term}' (case-insensitive) in history_text...")
    
    lower_text = history_text.lower()
    if search_term in lower_text:
        print(f"FOUND: '{search_term}' is present.")
        idx = lower_text.find(search_term)
        start = max(0, idx - 50)
        end = min(len(history_text), idx + 50)
        print(f"Context: ...{history_text[start:end]}...")
    else:
        print(f"NOT FOUND: '{search_term}' is NOT in the input.")
        
    # Check for emails
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', history_text)
    if emails:
        print(f"Found {len(emails)} potential emails: {emails[:5]}")
    else:
        print("No emails found.")

except Exception as e:
    print(f"Error: {e}")
