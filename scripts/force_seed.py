import sys
import os
import json
from tinydb import TinyDB

# Adjust path to find backend modules if needed, though we just need TinyDB here
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import DATA_DIR

def force_seed(target_db_path):
    print(f"Forcing seed to: {target_db_path}")
    seed_file = os.path.join(DATA_DIR, "seed_data.json")
    
    if not os.path.exists(seed_file):
        print(f"Seed file not found: {seed_file}")
        return

    with open(seed_file, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    db = TinyDB(target_db_path)
    
    # Drop tables
    db.drop_tables()
    
    # Insert data
    if 'components' in seed_data:
        db.table('components').insert_multiple(seed_data['components'])
        print(f"Inserted {len(seed_data['components'])} components.")
        
    if 'workflows' in seed_data:
        db.table('workflows').insert_multiple(seed_data['workflows'])
        print(f"Inserted {len(seed_data['workflows'])} workflows.")
        
    if 'steps' in seed_data:
        db.table('steps').insert_multiple(seed_data['steps'])
        print(f"Inserted {len(seed_data['steps'])} steps.")
        
    if 'prompts' in seed_data:
        db.table('prompts').insert_multiple(seed_data['prompts'])
        print(f"Inserted {len(seed_data['prompts'])} prompts.")

    print(f"Database at {target_db_path} seeded successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python force_seed.py <path_to_db>")
    else:
        force_seed(sys.argv[1])
