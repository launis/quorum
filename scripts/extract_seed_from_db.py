import json
import os

SOURCE_DB = r"c:\Users\risto\OneDrive\quorum\data\db_mock_restored.json"
TARGET_SEED = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def extract_and_save_seed():
    print(f"Reading from {SOURCE_DB}...")
    with open(SOURCE_DB, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    seed_data = {}
    
    # Tables to extract
    tables = ['components', 'steps', 'workflows']
    
    for table in tables:
        if table in db_data:
            print(f"Processing table: {table}")
            table_data = db_data[table]
            
            # TinyDB stores data as {"1": {...}, "2": {...}}
            # We need to convert this to a list [{...}, {...}] for seed_data.json
            # and for insert_multiple usage in seeder.
            
            print(f"  - Type: {type(table_data)}")
            if isinstance(table_data, dict):
                print(f"  - Keys sample: {list(table_data.keys())[:5]}")
                # Check if it's a TinyDB default table wrapper
                if "_default" in table_data and len(table_data) == 1:
                     print("  - Detected '_default' wrapper, drilling down...")
                     table_data = table_data["_default"]
                
                # Convert dict values to list
                items_list = list(table_data.values())
                seed_data[table] = items_list
                print(f"  - Extracted {len(items_list)} items.")
            elif isinstance(table_data, list):
                # Already a list (unlikely for raw TinyDB dump but possible)
                seed_data[table] = table_data
                print(f"  - Extracted {len(table_data)} items (already list).")
import json
import os

SOURCE_DB = r"c:\Users\risto\OneDrive\quorum\data\db_mock_restored.json"
TARGET_SEED = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def extract_and_save_seed():
    print(f"Reading from {SOURCE_DB}...")
    with open(SOURCE_DB, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    seed_data = {}
    
    # Tables to extract
    tables = ['components', 'steps', 'workflows']
    
    for table in tables:
        if table in db_data:
            print(f"Processing table: {table}")
            table_data = db_data[table]
            
            # TinyDB stores data as {"1": {...}, "2": {...}}
            # We need to convert this to a list [{...}, {...}] for seed_data.json
            # and for insert_multiple usage in seeder.
            
            print(f"  - Type: {type(table_data)}")
            if isinstance(table_data, dict):
                print(f"  - Keys sample: {list(table_data.keys())[:5]}")
                # Check if it's a TinyDB default table wrapper
                if "_default" in table_data and len(table_data) == 1:
                     print("  - Detected '_default' wrapper, drilling down...")
                     table_data = table_data["_default"]
                
                # Convert dict values to list
                items_list = list(table_data.values())
                seed_data[table] = items_list
                print(f"  - Extracted {len(items_list)} items.")
            elif isinstance(table_data, list):
                # Already a list (unlikely for raw TinyDB dump but possible)
                seed_data[table] = table_data
                print(f"  - Extracted {len(table_data)} items (already list).")
            else:
                print(f"  - Warning: Unexpected type for {table}: {type(table_data)}")
        else:
            print(f"Warning: Table {table} not found in source DB.")

    print(f"Saving to {TARGET_SEED}...")
    with open('data/extracted_seed.json', 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
    print("Seed data extracted to data/extracted_seed.json")

if __name__ == "__main__":
    extract_and_save_seed()
