
import json
import os

db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
target_id = "a2ff7f35-e79d-41f4-8c4a-c1a7ca8c38ce"

if not os.path.exists(db_path):
    print(f"DB file not found at {db_path}")
else:
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
            
        print(f"DB Keys: {list(db.keys())}")
        
        ex_data = None
        if 'executions' in db:
            if isinstance(db['executions'], dict):
                ex_data = db['executions'].get(target_id)
            elif isinstance(db['executions'], list):
                for x in db['executions']:
                    if x.get('id') == target_id:
                        ex_data = x
                        break
        
        if ex_data:
            print(f"ID: {ex_data.get('id')}")
            print(f"Status: {ex_data.get('status')}")
            print(f"Current Step Index: {ex_data.get('current_step_index')}")
            print("History:")
            for h in ex_data.get('history', []):
                print(f" - Step: {h.get('step_id')}, Status: {h.get('status')}")
            
            # Print last log if available
            logs = ex_data.get('logs', [])
            if logs:
                print("Last 3 Logs:")
                for l in logs[-3:]:
                    print(f" - {l}")
        else:
            print(f"Execution {target_id} not found.")

    except Exception as e:
        print(f"Error reading DB: {e}")
