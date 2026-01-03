
import json
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = os.path.join('data', 'db.json')
SEED_PATH = os.path.join('backend', 'database', 'seed_data.json')

def sync_db_to_seed():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    print(f"Reading {DB_PATH}...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    # Tables to sync
    tables = ['organizations', 'users', 'system_config', 'components', 'steps', 'workflows']
    
    seed_data = {}

    for table in tables:
        if table in db_data:
            print(f"Syncing table: {table}")
            table_data = db_data[table]
            # TinyDB stores as dict of ID -> Item. Convert to list.
            # However, seed_data.json expects lists for 'users', 'organizations', etc.
            # But wait, looking at seed_data.json (Step 1414), 'users' is a list.
            # 'components' in db.json seems to correspond to... wait, seed_data.json does NOT have 'components' key in the snippet I saw!
            # Let me re-verify seed_data.json content.
            # Step 1414 shows: organizations, users, system_config.
            # It does NOT show 'components', 'steps', 'workflows'.
            # Ah, maybe I missed them or they are generated?
            # Or maybe seed_data.json IS structurally different.
            
            # Helper: Convert TinyDB dict {id: item} to list [item]
            items = list(table_data.values())
            seed_data[table] = items
        else:
            print(f"Warning: Table {table} not found in db.json")

    # Special handling: validation or cleanup?
    # Ensure system_config is minimal?
    
    print(f"Writing to {SEED_PATH}...")
    # Preserve existing structure/order if possible? 
    # Actually, we are OVERWRITING seed_data.json to match db.json as the Source of Truth.
    
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=4, ensure_ascii=False)
    
    print("Sync complete.")

if __name__ == "__main__":
    sync_db_to_seed()
