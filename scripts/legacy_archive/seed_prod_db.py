import os
import sys

# Force REAL DB usage
# We set it to "False" explicitly.
os.environ["USE_MOCK_DB"] = "False"

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import get_db_path, DATA_DIR
import json
from backend.database.wrapper import get_db_client

def seed_prod_db():
    print("=== SEEDING PRODUCTION DATABASE ===")
    
    target_path = get_db_path()
    print(f"Target DB Path: {target_path}")
    
    if "db.json" not in str(target_path) or "mock" in str(target_path).lower():
        print(f"CRITICAL ERROR: Target path '{target_path}' does not look like production 'db.json'. Aborting.")
        return

    # 2. Correct path to seed_data.json
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed_file = os.path.join(project_root, "backend", "database", "seed_data.json")
    
    if not os.path.exists(seed_file):
        seed_file_alt = os.path.join(project_root, "data", "seed_data.json")
        if os.path.exists(seed_file_alt):
             seed_file = seed_file_alt
        else:
             print(f"Error: Seed file not found at {seed_file} or {seed_file_alt}")
             return

    print(f"Using Seed Source: {seed_file}")

    with open(seed_file, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    # 3. Drop Tables
    db_client = get_db_client()
    print("Dropping existing tables in Production DB...")
    db_client.db.drop_tables()
    
    # 4. Insert data
    tables_map = {
        'components': 'components',
        'workflows': 'workflows',
        'steps': 'steps',
        'prompts': 'prompts',
        'system_config': 'system_config'
    }

    count_total = 0
    for json_key, table_name in tables_map.items():
        if json_key in seed_data:
            table = db_client.table(table_name)
            items = seed_data[json_key]
            if hasattr(table, '_table'):
                 table._table.insert_multiple(items)
            else:
                 for item in items:
                     table.insert(item)
            count = len(items)
            count_total += count
            print(f"  - Inserted {count} items into '{table_name}'.")

    print(f"=== SUCCESS: Populated Production DB ({target_path}) with {count_total} items. ===")

if __name__ == "__main__":
    seed_prod_db()
