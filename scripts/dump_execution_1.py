
import json
import os

db_path = r"c:\src\quorum\data\db.json"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get('executions', {})
    if '1' in executions:
        run = executions['1']
        print(f"--- Execution stored at key '1' ---")
        print(json.dumps(run, indent=2))
                
except Exception as e:
    print(f"Error: {e}")
