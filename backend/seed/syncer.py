import json
import os
import sys
from typing import List, Dict, Any

def sync_db_to_seed():
    """
    Reads the current active database (Local/Prod) and exports the configuration 
    tables back to seed_data.json.
    Excludes execution history.
    """
    from backend.settings import get_settings
    settings = get_settings()

    # Determine source DB path
    # Usually we want to sync from the "Prod" (Local Persistent) DB if running this script,
    # because that's where we make changes. 
    # However, if Env var USE_MOCK_DB is true, we might be syncing from Mock.
    # But usually Sync = Prod -> Seed.
    
    # We'll use settings.start_db_path effectively.
    # But we want to be explicit. If this runs via wrapper that sets USE_MOCK_DB=false,
    # then start_db_path is prod_db_path.
    
    source_path = settings.start_db_path
    target_path = settings.seed_data_path

    if not os.path.exists(source_path):
        print(f"[Syncer] Error: Source DB {source_path} not found.")
        return

    print(f"[Syncer] Reading from {source_path}...")
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
    except Exception as e:
        print(f"[Syncer] Failed to read DB: {e}")
        return

    # Tables to sync (Configuration only, NO history/executions)
    tables_to_sync = [
        'organizations', 
        'users', 
        'system_config', 
        'components', 
        'steps', 
        'workflows', 
        'knowledge_base',
        'banned_phrases',
        'model_registry',
        'dimensions'
    ]
    
    # Check what tables seeder supports. Seeder supports:
    # components, steps, workflows, banned_phrases, system_config, knowledge_base, organizations, users, model_registry.
    # So I should include ALL of these if I want a complete seed.
    
    seed_data = {}

    for table in tables_to_sync:
        if table in db_data:
            print(f"[Syncer] Syncing table: {table}")
            table_data = db_data[table]
            
            # TinyDB stores data as a dict of { "1": item, "2": item }.
            # seed_data.json expects a list [ item, item ].
            # We must convert values to list.
            if isinstance(table_data, dict):
                items = list(table_data.values())
                seed_data[table] = items
            elif isinstance(table_data, list): # Should not happen in TinyDB JSON but just in case
                seed_data[table] = table_data
        else:
            # If table missing in DB, check if we should keep it empty or warn
            # print(f"[Syncer] Note: Table {table} not in source DB.")
            pass

    print(f"[Syncer] Writing to {target_path}...")
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(seed_data, f, indent=4, ensure_ascii=False)
        print("[Syncer] Sync complete. Seed file updated.")
    except Exception as e:
        print(f"[Syncer] Failed to write seed file: {e}")

if __name__ == "__main__":
    sync_db_to_seed()
