import json
from deepdiff import DeepDiff
import sys

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_kb(kb_data):
    """Normalize KB data (dict vs list) to a dict of items by ID."""
    if isinstance(kb_data, list):
        return {item['id']: item for item in kb_data if 'id' in item}
    elif isinstance(kb_data, dict):
        # TinyDB format: {"1": {...}, "2": {...}}
        # We need to map by 'id' field inside the item
        return {v['id']: v for k, v in kb_data.items() if 'id' in v}
    return {}

def normalize_components(comp_data):
    """Normalize Components data."""
    if isinstance(comp_data, list):
         return {item['id']: item for item in comp_data if 'id' in item}
    elif isinstance(comp_data, dict):
         return {v['id']: v for k, v in comp_data.items() if 'id' in v}
    return {}

def clean_item(item):
    """Remove runtime fields for comparison."""
    runtime_fields = ['ingested_at', 'job_id', 'vector_id', 'metadata'] 
    # Metadata often varies (timestamps), so excluding it for strict content check might be needed
    # But let's keep metadata for now and see if it's the only diff.
    # Actually, TinyDB might add internal fields? No, usually clean.
    
    clean = item.copy()
    for field in runtime_fields:
        if field in clean:
            del clean[field]
    return clean

def verify_parity():
    seed_path = "c:/src/quorum/backend/seed/seed_data.json"
    db_path = "c:/src/quorum/data/db.json"
    
    print(f"Loading {seed_path}...")
    seed = load_json(seed_path)
    
    print(f"Loading {db_path}...")
    db = load_json(db_path)
    
    # 1. Compare Knowledge Base
    print("\n--- Comparing Knowledge Base ---")
    seed_kb = normalize_kb(seed.get('knowledge_base', []))
    db_kb = normalize_kb(db.get('knowledge_base', {}))
    
    seed_ids = set(seed_kb.keys())
    db_ids = set(db_kb.keys())
    
    missing_in_db = seed_ids - db_ids
    missing_in_seed = db_ids - seed_ids
    
    if missing_in_db:
        print(f"Missing in DB: {len(missing_in_db)} items")
    if missing_in_seed:
        print(f"Extra in DB: {len(missing_in_seed)} items")
        
    common_ids = seed_ids.intersection(db_ids)
    print(f"Checking {len(common_ids)} common items...")
    
    diff_count = 0
    for cid in common_ids:
        s_item = clean_item(seed_kb[cid])
        d_item = clean_item(db_kb[cid])
        
        diff = DeepDiff(s_item, d_item, ignore_order=True)
        if diff:
            print(f"Diff in Item {cid}: {diff}")
            diff_count += 1
            if diff_count > 5:
                print("... stopping after 5 diffs ...")
                break
                
    if diff_count == 0 and not missing_in_db and not missing_in_seed:
        print("Knowledge Base: MATCH")
    else:
        print("Knowledge Base: MISMATCH")

    # 2. Compare Components
    print("\n--- Comparing Components ---")
    seed_comp = normalize_components(seed.get('components', []))
    db_comp = normalize_components(db.get('components', {}))
    
    s_c_ids = set(seed_comp.keys())
    d_c_ids = set(db_comp.keys())
    
    print(f"Seed: {len(s_c_ids)}, DB: {len(d_c_ids)}")
    
    # ... similiar check ...
    
    print("\nDone.")

if __name__ == "__main__":
    try:
        verify_parity()
    except Exception as e:
        print(f"Error: {e}")
