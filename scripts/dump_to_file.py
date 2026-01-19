
import json
import os

db_path = r"c:\src\quorum\data\db.json"
out_path = r"c:\src\quorum\execution_dump.json"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get('executions', {})
    if '1' in executions:
        run = executions['1']
        with open(out_path, 'w', encoding='utf-8') as out:
            json.dump(run, out, indent=2)
        print(f"Dumped to {out_path}")
                
except Exception as e:
    print(f"Error: {e}")
