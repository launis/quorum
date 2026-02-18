import json
import os
import shutil

SEED_PATH = os.path.join("backend", "seed", "seed_data.json")

def restore_seed_structure():
    if not os.path.exists(SEED_PATH):
        print(f"File not found: {SEED_PATH}")
        return

    # Backup
    shutil.copy(SEED_PATH, SEED_PATH + ".bak_struct_restore")
    print(f"Backed up {SEED_PATH} to {SEED_PATH}.bak_struct_restore")

    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    changes_made = False

    # Check for TinyDB wrapping (e.g. "_default" key)
    if "_default" in data:
        print("Detected TinyDB wrapping ('_default' key). Unwraping...")
        data = data["_default"]
        changes_made = True

    # Collections expected to be LISTS in seed data
    collections = [
        "workflows", 
        "components", 
        "steps", 
        "system_config", 
        "knowledge_base", 
        "dimensions", 
        "organizations", 
        "users"
    ]

    for col in collections:
        if col in data:
            if isinstance(data[col], dict):
                print(f"Converting '{col}' from DICT to LIST...")
                # TinyDB stores items as { "1": {...}, "2": {...} }
                # We need [ {...}, {...} ]
                # We should sort by ID if possible to keep order stable, or just values.
                # Use values() to get the objects.
                items_list = list(data[col].values())
                
                # Optional: Sort by ID for stability
                try:
                    items_list.sort(key=lambda x: str(x.get("id", "")))
                except Exception:
                    pass # Best effort sort

                data[col] = items_list
                changes_made = True
            elif isinstance(data[col], list):
                print(f"'{col}' is already a LIST. Correct.")
            else:
                print(f"Warning: '{col}' is neither list nor dict. Skipping.")

    if changes_made:
        with open(SEED_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully restored seed structure in {SEED_PATH}")
    else:
        print("No structural changes needed.")

if __name__ == "__main__":
    restore_seed_structure()
