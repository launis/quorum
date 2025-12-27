
import json
import os

DB_PATHS = [
    "backend/database/db_mock.json",
    "backend/database/seed_data.json",
    "backend/database/db.json"
]

def fix_db(path):
    if not os.path.exists(path):
        print(f"Skipping {path}, not found.")
        return

    print(f"Processing {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading {path}: {e}")
        return

    changed = False
    
    # TinyDB structure vs Seed Data structure
    # Seed data usually has "components": { "1": {...}, "2": {...} }
    # TinyDB export has "_default": { "1": {...} } OR specific table names.
    
    # We look for ANY dictionary that looks like a table of components.
    # In seed_data.json it's "components".
    # In db_mock.json it's "components" (based on previous view).
    
    target_keys = ["components"]
    
    for key in target_keys:
        if key in data:
            table = data[key]
            to_delete = []
            
            for item_id, item in table.items():
                if not isinstance(item, dict):
                    continue
                
                # Check for missing ID
                if 'id' not in item or item['id'] is None or item['id'] == "":
                    # Try to recover from name
                    if 'name' in item and item['name']:
                        item['id'] = item['name']
                        print(f"  Fixed ID for component: {item['name']}")
                        changed = True
                    else:
                        print(f"  Found garbage component (key={item_id}), deleting: {item}")
                        to_delete.append(item_id)
            
            for item_id in to_delete:
                del table[item_id]
                changed = True
                
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Saved changes to {path}.")
    else:
        print(f"No changes needed for {path}.")

if __name__ == "__main__":
    for p in DB_PATHS:
        fix_db(p)
