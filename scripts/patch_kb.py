
import json
import os

seed_path = r'c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json'
db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'

try:
    # 1. Read Seed Data
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
    
    # 2. Extract Knowledge Base from seed
    system_config = seed_data.get('system_config', [])
    knowledge_base = None
    
    # Handling list format in seed_data
    if isinstance(system_config, list):
        for item in system_config:
            if item.get('type') == 'knowledge_base':
                knowledge_base = item
                break
    
    if not knowledge_base:
        print("Error: Knowledge Base not found in seed_data.json!")
        exit(1)

    print(f"Found Knowledge Base in seed: {knowledge_base.get('name')}")
    print(f"Concepts count: {len(knowledge_base.get('concepts', {}))}")

    # 3. Read Current DB
    if not os.path.exists(db_path):
        print("Error: db.json not found!")
        exit(1)
        
    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
        
    # 4. Patch DB
    if 'system_config' not in db_data:
        db_data['system_config'] = {}
        
    # TinyDB 'system_config' is strictly a dict of ID -> Item (e.g. "1": {...})
    # We need to find the next available ID or overwrite if exists.
    
    # Check if 'knowledge_base' already exists by ID
    target_key = None
    for key, val in db_data['system_config'].items():
        if val.get('type') == 'knowledge_base':
            target_key = key
            break
            
    if target_key:
        print(f"Updating existing Knowledge Base at key '{target_key}'...")
        db_data['system_config'][target_key] = knowledge_base
    else:
        # Find max ID
        max_id = 0
        for k in db_data['system_config'].keys():
            try:
                kid = int(k)
                if kid > max_id: max_id = kid
            except:
                pass
        new_key = str(max_id + 1)
        print(f"Inserting new Knowledge Base at key '{new_key}'...")
        db_data['system_config'][new_key] = knowledge_base

    # 5. Save DB
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, indent=4)
        
    print("Successfully patched db.json with Knowledge Base.")

except Exception as e:
    print(f"Script failed: {e}")
    import traceback
    traceback.print_exc()
