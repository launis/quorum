import os
import sys

# Set environment variable to force Mock DB usage ONLY if not already set
if "USE_MOCK_DB" not in os.environ:
    os.environ["USE_MOCK_DB"] = "True"

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.engine import WorkflowEngine
from backend.config import get_db_path, DATA_DIR
import json

from backend.database.wrapper import get_db_client

def seed_mock_db():
    print("Seeding MOCK Database...")
    
    # 1. Get DB Client directly
    db_client = get_db_client()
    print(f"Target DB Path: {get_db_path()}")

    # 2. Correct path to seed_data.json
    # It is in <project_root>/data/seed_data.json
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed_file = os.path.join(project_root, "data", "seed_data.json")
    
    if not os.path.exists(seed_file):
        print(f"Error: Seed file not found at {seed_file}")
        return

    with open(seed_file, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    # 3. Clear existing tables
    # Access the underlying TinyDB instance to drop tables
    db_client.db.drop_tables()
    
    # 4. Insert data using wrapper methods (or direct table access if wrapper lacks bulk insert)
    # The wrapper exposes .table(name) which returns a TinyDB table-like object
    
    tables_map = {
        'components': 'components',
        'workflows': 'workflows',
        'steps': 'steps',
        'prompts': 'prompts',
        'system_config': 'system_config'
    }

    for json_key, table_name in tables_map.items():
        if json_key in seed_data:
            table = db_client.table(table_name)
            # Use internal _table for bulk insert efficiency in TinyDB
            if hasattr(table, '_table'):
                 table._table.insert_multiple(seed_data[json_key])
            else:
                 # Fallback
                 for item in seed_data[json_key]:
                     table.insert(item)
            print(f"Inserted {len(seed_data[json_key])} items into '{table_name}'.")


    print("Mock Database seeded successfully.")

if __name__ == "__main__":
    seed_mock_db()
