import sys
import os
from tinydb import TinyDB, Query

# Adjust path to find backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_user():
    db_path = "data/db.json"
    print(f"Checking {db_path}...")
    
    if not os.path.exists(db_path):
        print("ERROR: db.json not found!")
        return

    db = TinyDB(db_path)
    users_table = db.table("users")
    
    print(f"Total Users: {len(users_table.all())}")
    
    User = Query()
    root_master = users_table.get(User.uid == 'root_master')
    
    if root_master:
        print("SUCCESS: Found root_master:")
        print(root_master)
    else:
        print("FAILURE: root_master NOT found in users table.")
        # List all UIDs
        all_uids = [u.get('uid') for u in users_table.all()]
        print(f"Existing UIDs: {all_uids}")

if __name__ == "__main__":
    check_user()
