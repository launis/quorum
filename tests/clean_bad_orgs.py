
from tinydb import TinyDB, Query
import os

def clean_orgs():
    db_path = "data/db.json"
    if not os.path.exists(db_path):
        db_path = "db.json"

    print(f"Cleaning {db_path}...")
    db = TinyDB(db_path)
    org_table = db.table('organizations')
    
    # 1. Remove 'acme' if it exists
    Q = Query()
    removed = org_table.remove(Q.id == 'acme')
    print(f"Removed {removed} 'acme' organizations.")
    
    # 2. Verify remaining
    orgs = org_table.all()
    print(f"Current Organizations: {[o['id'] for o in orgs]}")

if __name__ == "__main__":
    clean_orgs()
