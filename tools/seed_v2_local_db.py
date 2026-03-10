import json
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend_v2.database.wrapper import TinyDBClient

def seed_db():
    db_path = "data/db_v2.json"
    seed_path = "backend_v2/seed/seed_data.json"
    
    print(f"Reading from {seed_path}...")
    with open(seed_path, "r", encoding="utf-8") as f:
        seed_data = json.load(f)
        
    print(f"Initializing TinyDB at {db_path}...")
    db_client = TinyDBClient(db_path)
    
    
    for collection_name, items in seed_data.items():
        if isinstance(items, list):
            print(f"Inserting {len(items)} items into {collection_name}...")
            table = db_client.table(collection_name)
            for index, item in enumerate(items, start=1):
                # TinyDB requires doc_id to be an integer. It doesn't strictly matter if we just use insert.
                # However, for consistency, we'll just insert raw dictionaries.
                table.insert(item)
                
    print(f"Successfully seeded {db_path}!")

if __name__ == "__main__":
    seed_db()
