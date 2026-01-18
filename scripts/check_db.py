
import json
import os

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
        # TinyDB stores as dict of ID -> Record, or sometimes just list? 
        # TinyDB default is usually: {"_default": {"1": {...}, "2": {...}}} OR if tables are used: {"users": {"1": ...}}
        # But Wrapper might abstract this. Let's inspect the structure of 'users'.
        print(f"Users type: {type(users)}")
        
        found_root = False
        if isinstance(users, dict):
            for key, val in users.items():
                if val.get("uid") == "root_master":
                    print(f"FOUND root_master: {val}")
                    found_root = True
                    break
        
        if not found_root:
            print("root_master NOT found in users table.")
    else:
        print("'users' table NOT found in db.json")

except Exception as e:
    print(f"Error reading JSON: {e}")
