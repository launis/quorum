import json
import os

FILES_TO_CLEAN = [
    'backend/seed/seed_data.json',
    'data/db.json'
]

def clean_file(path):
    if not os.path.exists(path):
        print(f"Skipping {path} (Not found)")
        return

    print(f"--- Cleaning {path} ---")
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return

    # Check structure
    workflows = []

    # helper for db.json which might have 'workflows': {'1': {...}} structure vs list
    is_dict_like = False

    if 'workflows' in data:
        w_data = data['workflows']
        if isinstance(w_data, list):
            workflows = w_data
        elif isinstance(w_data, dict):
            # TinyDB style: {"1": {...}, "2": {...}}
            is_dict_like = True
            workflows = w_data.values()

    removed_count = 0
    for wf in workflows:
        if 'default_model_mapping' in wf:
            del wf['default_model_mapping']
            removed_count += 1

    if removed_count > 0:
        print(f"Removed 'default_model_mapping' from {removed_count} workflows.")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            print("File saved.")
    else:
        print("No legacy mappings found.")

if __name__ == "__main__":
    for f in FILES_TO_CLEAN:
        clean_file(f)
