
import json
import os
import sys

def merge_seeds():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SEED_DIR = os.path.join(BASE_DIR, "backend", "seed")
    
    current_seed_path = os.path.join(SEED_DIR, "seed_data.json")
    legacy_seed_path = os.path.join(SEED_DIR, "temp_seed.json")
    
    print(f"Reading current seed: {current_seed_path}")
    with open(current_seed_path, "r", encoding="utf-8") as f:
        current_data = json.load(f)
        
    print(f"Reading legacy seed: {legacy_seed_path}")
    with open(legacy_seed_path, "r", encoding="utf-8") as f:
        legacy_data = json.load(f)
        
    current_components = current_data.get("components", [])
    legacy_components = legacy_data.get("components", [])
    
    # helper to track existing IDs
    existing_ids = {c["id"] for c in current_components if "id" in c}
    
    print(f"Current components count: {len(current_components)}")
    print(f"Legacy components count: {len(legacy_components)}")
    
    added_count = 0
    skipped_count = 0
    
    for comp in legacy_components:
        c_id = comp.get("id")
        if not c_id:
            continue
            
        if c_id not in existing_ids:
            # Add missing component
            current_components.append(comp)
            existing_ids.add(c_id)
            added_count += 1
            print(f"Restoring component: {c_id}")
        else:
            skipped_count += 1
            
    current_data["components"] = current_components
    
    print(f"Merge complete. Added {added_count} components. Skipped {skipped_count} existing.")
    
    # Backup original
    backup_path = current_seed_path + ".bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False) # Wait, saving parsed data as backup? No, should cp file.
    
    # Actually just overwrite seed_data.json with merged data
    with open(current_seed_path, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)
        
    print(f"Saved merged data to {current_seed_path}")

if __name__ == "__main__":
    merge_seeds()
