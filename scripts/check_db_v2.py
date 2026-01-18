
import json
import os
import sys

# Force utf-8 output for Windows console
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"c:\src\quorum\data\db.json"

if not os.path.exists(db_path):
    print(f"Error: {db_path} does not exist.")
    exit(1)

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Root keys: {list(data.keys())}")
    
    if "users" in data:
        users = data["users"]
        print(f"User count: {len(users)}")
        print(f"Users data type: {type(users)}")
        print("--- USERS DUMP ---")
        print(json.dumps(users, indent=2, ensure_ascii=False))
        print("------------------")
        
        # Check for root_master
        found = False
        if isinstance(users, dict):
            # TinyDB 'default' table format: {"_default": {"1": {...}}}
            # Or if custom table: {"users": {"1": {...}}}
            # But here 'users' is a key in the root dict, suggesting it IS the table content (if using table-per-key generic JSON)
            # OR 'users' is the table name and the value is the dict of records.
            # TinyDB structure: {"table_name": {"doc_id": {record}}}
            
            for k, v in users.items():
                if isinstance(v, dict) and v.get("uid") == "root_master":
                    found = True
                    print("SUCCESS: root_master found!")
                    break
        
        if not found:
            print("FAILURE: root_master NOT found in users dump.")
            
    else:
        print("'users' key NOT found in db.json")

except Exception as e:
    print(f"Error reading JSON: {e}")
