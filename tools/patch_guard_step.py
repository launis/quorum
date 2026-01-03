
import json
from tinydb import TinyDB, Query, where
import os

SEED_FILE = "backend/database/seed_data.json"
DB_FILE = "data/db.json"

def patch_guard_component():
    print(f"Reading seed data from {SEED_FILE}...")
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
    
    # 1. Find the TASK_GUARD definition in components
    # (Debug script confirmed it's in 'components')
    components = seed_data.get('components', [])
    task_guard = next((item for item in components if item.get('id') == 'TASK_GUARD'), None)

    if not task_guard:
        print("❌ Error: TASK_GUARD component not found in seed_data['components']!")
        return

    print("Found TASK_GUARD in seed data.")
    print(f"Content snippet: {task_guard['content'][:50]}...")
    
    # 2. Update it in the LIVE database
    print(f"Opening database {DB_FILE}...")
    db = TinyDB(DB_FILE)
    
    # In db.json, components are usually in 'system_config' OR 'components' depending on seeder version.
    # But seeder.py usually dumps everything into system_config_table or specific tables.
    # Target components table which repository.py reads from
    # (Previously we tried system_config, but that was ignored)
    config_table = db.table('components') 
    
    Config = Query()
    # Upsert based on ID 'TASK_GUARD'
    config_table.upsert(task_guard, Config.id == 'TASK_GUARD')
    
    print(f"✅ Successfully upserted TASK_GUARD into 'components' table.")

if __name__ == "__main__":
    patch_guard_component()
