
import json
import os
import sys

def merge_inverse():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SEED_DIR = os.path.join(BASE_DIR, "backend", "seed")
    
    current_seed_path = os.path.join(SEED_DIR, "seed_data.json")
    # Using temp_seed.json which is the one downloaded from GitHub (Legacy/Base)
    legacy_seed_path = os.path.join(SEED_DIR, "temp_seed.json") 
    
    print(f"Reading Current (Structure Source): {current_seed_path}")
    with open(current_seed_path, "r", encoding="utf-8") as f:
        current_data = json.load(f)
        
    print(f"Reading Legacy/GitHub (Content Base): {legacy_seed_path}")
    with open(legacy_seed_path, "r", encoding="utf-8") as f:
        base_data = json.load(f)
        
    # 1. OVERWRITE Structural Sections from Current
    # We trust today's structure (Workflows, Steps, IAM) more than legacy
    print("Overwriting 'workflows' with Current version...")
    base_data["workflows"] = current_data.get("workflows", [])
    
    print("Overwriting 'steps' with Current version...")
    base_data["steps"] = current_data.get("steps", [])
    
    print("Overwriting 'users' with Current version...")
    base_data["users"] = current_data.get("users", [])
    
    print("Overwriting 'organizations' with Current version...")
    base_data["organizations"] = current_data.get("organizations", [])
    
    # 2. MERGE Components (Preserve Legacy Content, Add New)
    base_components = base_data.get("components", [])
    current_components = current_data.get("components", [])
    
    base_ids = {c["id"] for c in base_components if "id" in c}
    
    added_count = 0
    
    print("Merging NEW components from Current -> Base...")
    for comp in current_components:
        c_id = comp.get("id")
        if not c_id:
            continue
            
        if c_id not in base_ids:
            # This is a NEW component added today (e.g. DocumentProcessor or new Config)
            base_components.append(comp)
            base_ids.add(c_id)
            added_count += 1
            print(f"Adding NEW component: {c_id}")
            
    base_data["components"] = base_components
    
    print(f"Inverse Merge complete. Added {added_count} new components to Base.")
    
    # Save to seed_data.json
    with open(current_seed_path, "w", encoding="utf-8") as f:
        json.dump(base_data, f, indent=4, ensure_ascii=False)
        
    print(f"Saved merged data to {current_seed_path}")

if __name__ == "__main__":
    merge_inverse()
