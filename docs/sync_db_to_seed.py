import json
import shutil
import os

SOURCE_DB = r"c:\Users\risto\OneDrive\quorum\data\db.json"
MOCK_DB = r"c:\Users\risto\OneDrive\quorum\backend\database\db_mock.json"
SEED_DATA = r"c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json"

def sync():
    print(f"Reading active database from {SOURCE_DB}...")
    try:
        with open(SOURCE_DB, 'r', encoding='utf-8') as f:
            full_db = json.load(f)
    except FileNotFoundError:
        print("Error: Source DB not found.")
        return

    # 1. Update Mock DB (Direct clone)
    print(f"Creating Backup/Mock to {MOCK_DB}...")
    shutil.copy2(SOURCE_DB, MOCK_DB)
    print(" - Mock DB updated successfully.")

    # 2. Update Seed Data (Filtered export)
    print(f"Updating Seed Data {SEED_DATA}...")
    
    # We define strictly which tables constitute the 'Seed' (Knowledge + Config).
    # We EXCLUDE ephemeral data like 'executions', 'files', 'jobs'.
    seed_tables = [
        "system_config",
        "agents", 
        "workflows", 
        "components", 
        "concepts", 
        "references", 
        "claims" 
    ]
    
    new_seed = {}
    
    for table in seed_tables:
        if table in full_db:
            table_data = full_db[table]
            new_seed[table] = table_data
            # Count items (TinyDB tables are dicts of id->item)
            count = len(table_data)
            print(f" - Preserved {count} items for table '{table}'")
        else:
            print(f" - Warning: Table '{table}' not found in source DB (might be empty).")

    # Write the clean seed file
    with open(SEED_DATA, 'w', encoding='utf-8') as f:
        json.dump(new_seed, f, indent=4, ensure_ascii=False)
    
    print("\nSUCCESS: Knowledge Base and Configs have been saved to seed_data.json.")
    print("History/Executions were intentionally excluded from the seed to keep it clean.")

if __name__ == "__main__":
    sync()
