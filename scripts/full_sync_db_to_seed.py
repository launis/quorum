import json
import os
import shutil

DB_PATH = 'c:/src/quorum/data/db.json'
SEED_PATH = 'c:/src/quorum/backend/seed/seed_data.json'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def to_list(data):
    if isinstance(data, dict):
        return list(data.values())
    elif isinstance(data, list):
        return data
    else:
        return []

def full_sync():
    print(f"Loading DB from {DB_PATH}...")
    db = load_json(DB_PATH)
    print(f"Loading Seed from {SEED_PATH}...")
    seed = load_json(SEED_PATH)

    # 1. Workflows
    if 'workflows' in db:
        print("Syncing workflows...")
        seed['workflows'] = to_list(db['workflows'])
    
    # 2. Components (and KB)
    comps = []
    if 'components' in db:
        comps = to_list(db['components'])
        print(f"Got {len(comps)} components from DB.")
    
    # Check for KB in Root "2" if not in comps
    kb_found = False
    for c in comps:
        if c.get('id') == 'knowledge_base':
            kb_found = True
            break
            
    if not kb_found and '2' in db:
        print("Injecting Root '2' (Knowledge Base) into components...")
        kb_data = db['2']
        # Ensure it has right ID just in case
        if kb_data.get('id') != 'knowledge_base':
             kb_data['id'] = 'knowledge_base' # Force ID if missing (unlikely)
        comps.append(kb_data)
        
    seed['components'] = comps
    print(f"Total Components in Seed: {len(comps)}")

    # 3. System Config
    if 'system_config' in db:
        print("Syncing system_config...")
        seed['system_config'] = to_list(db['system_config'])

    # Backup & Save
    shutil.copy(SEED_PATH, SEED_PATH + ".bak_v2")
    save_json(SEED_PATH, seed)
    print("Saved updated seed_data.json")

if __name__ == "__main__":
    full_sync()
