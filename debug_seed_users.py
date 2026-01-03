import json
from tinydb import TinyDB, Query, where

db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
seed_path = r'c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json'

try:
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
        
    db = TinyDB(db_path, encoding='utf-8')
    users_table = db.table('users')
    User = Query()
    
    print("Starting manual seed...")
    for item in seed_data.get('users', []):
        uid = item.get('uid')
        print(f"Processing {uid}...")
        try:
            users_table.upsert(item, User.uid == uid)
            print(f"  Upserted {uid}")
        except Exception as e:
            print(f"  Failed {uid}: {e}")
            
    print("Done.")
    
except Exception as e:
    print(f"Global Error: {e}")
