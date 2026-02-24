import json
from pathlib import Path

def restore_input_keys():
    base_dir = Path(r"c:\src\quorum")
    files_to_check = [
        base_dir / "backend" / "seed" / "seed_data.json",
        base_dir / "data" / "db.json"
    ]

    for file_path in files_to_check:
        if not file_path.exists():
            print(f"Skipping {file_path}, does not exist.")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Build reverse map: UUID -> slug
        uuid_to_slug = {}
        for collection in data.values():
            if isinstance(collection, list):
                for item in collection:
                    if isinstance(item, dict) and 'id' in item and 'slug' in item:
                        uuid_to_slug[item['id']] = item['slug']

        # Extra hardcoded fallback if standard map misses it:
        # Pydantic explicitly expects "step_analyst", "step_guard", etc.
        # We can just revert any key that is a UUID back to the known step slugs.
        
        changes_made = 0
        steps = data.get('steps', [])
        for step in steps:
            if 'inputs' not in step:
                continue
            
            new_inputs = {}
            for k, v in step['inputs'].items():
                if k in uuid_to_slug:
                    old_slug = uuid_to_slug[k]
                    new_inputs[old_slug] = v
                    changes_made += 1
                else:
                    new_inputs[k] = v
            
            step['inputs'] = new_inputs

        if changes_made > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Restored {changes_made} input keys in {file_path.name}")
        else:
            print(f"No changes needed for {file_path.name}")

if __name__ == '__main__':
    restore_input_keys()
