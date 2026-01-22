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

def sync():
    print(f"Loading DB from {DB_PATH}...")
    db = load_json(DB_PATH)
    print(f"Loading Seed from {SEED_PATH}...")
    seed = load_json(SEED_PATH)

    # 1. Sync System Config (Model Registry)
    if 'system_config' in db:
        print("Found system_config in DB.")
        # DB system_config might be dict or list. Seed usually expects dict?
        # Let's inspect DB type
        sc_db = db['system_config']
        
        # If seed doesn't have it, we create it.
        # We need to know if seed expects dict or list.
        # Looking at seed_data.json structure (lines 1-50), it uses lists for organizations, users.
        # But 'system_config' in db.json is {"1": ...}.
        # We will copy it as is, or convert if seed has a preference.
        # Since seed didn't have it, we'll assume DB structure is correct for the backend.
        
        seed['system_config'] = sc_db
        print("Synced system_config.")
    else:
        print("Warning: system_config not found in DB!")

    # 2. Sync Knowledge Base (Component 2)
    # Check if DB has better knowledge base
    # DB components -> "2"
    kb_db = None
    if 'components' in db:
        cmds = db['components']
        if isinstance(cmds, dict) and '2' in cmds:
            kb_db = cmds['2']
        elif isinstance(cmds, list):
             for c in cmds:
                 if c.get('id') == 'knowledge_base':
                     kb_db = c
                     break
    
    # Fallback root check
    if not kb_db and '2' in db:
        kb_db = db['2']

    if kb_db:
        print("Found Knowledge Base in DB.")
        # Find in Seed
        seed_comps = seed.get('components', [])
        found_idx = -1
        for i, c in enumerate(seed_comps):
            if c.get('id') == 'knowledge_base' or c.get('type') == 'knowledge_base':
                found_idx = i
                break
        
        if found_idx >= 0:
            print(f"Updating existing Knowledge Base in Seed (Index {found_idx})")
            # Preserve some fields? Or overwrite?
            # DB seems "richer" according to user. Let's overwrite.
            # But we must ensure format of 'kb_db' matches valid component structure.
            # In db.json, it was {"2": ...}. kb_db is the value.
            seed_comps[found_idx] = kb_db
        else:
            print("Adding new Knowledge Base to Seed components.")
            seed_comps.append(kb_db)
        
        seed['components'] = seed_comps
    else:
        print("Warning: Knowledge Base not found in DB!")

    # Save
    backup_path = SEED_PATH + ".bak"
    shutil.copy(SEED_PATH, backup_path)
    print(f"Backed up seed to {backup_path}")
    
    save_json(SEED_PATH, seed)
    print("Saved updated seed_data.json")

if __name__ == "__main__":
    sync()
