import json
import os
from tinydb import TinyDB

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'db.json')
SEED_DATA_PATH = os.path.join(DATA_DIR, 'seed_data.json')

def update_seed_data():
    print(f"Updating {SEED_DATA_PATH} from {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("Error: Database file not found.")
        return

    db = TinyDB(DB_PATH, encoding='utf-8')
    components_table = db.table('components')
    steps_table = db.table('steps')
    workflows_table = db.table('workflows')

    # Load existing seed data to preserve structure if needed
    seed_data = {}
    if os.path.exists(SEED_DATA_PATH):
        with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
            try:
                seed_data = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Existing seed_data.json is corrupt. Starting fresh.")
                seed_data = {"components": [], "steps": [], "workflows": []}
    else:
        seed_data = {"components": [], "steps": [], "workflows": []}

    # Update lists from DB
    # We want to keep the seed data clean.
    
    # 1. Components
    # We fetch all components. 
    # Note: For templated components, the 'content' field in DB might be the *rendered* content.
    # If we save this back to seed_data, and then run seeder.py, seeder.py might re-render it from template.
    # However, for our NEW components (References, Rules, Mandates created via API), they are NOT in templates.
    # So we MUST save their content.
    # The safest approach for a "snapshot" is to save everything.
    
    all_components = components_table.all()
    print(f"  Found {len(all_components)} components.")
    seed_data['components'] = all_components

    # 2. Steps
    all_steps = steps_table.all()
    print(f"  Found {len(all_steps)} steps.")
    seed_data['steps'] = all_steps

    # 3. Workflows
    all_workflows = workflows_table.all()
    print(f"  Found {len(all_workflows)} workflows.")
    seed_data['workflows'] = all_workflows

    # Save back to file
    try:
        with open(SEED_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)
        print("Successfully updated seed_data.json")
    except Exception as e:
        print(f"Error saving seed data: {e}")

if __name__ == "__main__":
    update_seed_data()
