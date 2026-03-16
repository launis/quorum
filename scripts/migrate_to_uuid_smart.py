import json
import uuid
from pathlib import Path


def run_smart_migration():
    base_dir = Path(r"c:\src\quorum\backend\seed")
    source_file = base_dir / "seed_data copy.json"
    target_file = base_dir / "seed_data.json"

    with open(source_file, encoding='utf-8') as f:
        data = json.load(f)

    # 1. First Pass: Generate mapping and update IDs/Slugs
    id_map = {}

    # We will also track steps to update their $ variable references
    step_id_map = {}

    for collection_name, items in data.items():
        if isinstance(items, list):
            for item in items:
                old_id = item.get('id')
                # Users edge case
                if collection_name == 'users' and 'uid' in item:
                    old_id = item.pop('uid')

                if old_id:
                    # Generate deterministically random new UUID
                    new_id = str(uuid.uuid4())
                    id_map[old_id] = new_id

                    if collection_name == 'steps':
                        step_id_map[old_id] = new_id

                    item['id'] = new_id
                    item['slug'] = old_id

        elif isinstance(items, dict) and collection_name == "system_config":
            # For system configs, they have an 'id' inside
            if 'id' in items:
                old_id = items['id']
                new_id = str(uuid.uuid4())
                id_map[old_id] = new_id
                items['slug'] = old_id
                items['id'] = new_id

        elif isinstance(items, list) and collection_name == "system_config": # if it's a list
             for item in items:
                old_id = item.get('id')
                if old_id:
                    new_id = str(uuid.uuid4())
                    id_map[old_id] = new_id
                    item['id'] = new_id
                    item['slug'] = old_id

    # Add hardcoded "system" organization to map in case it's not in the array but referenced
    if "system" not in id_map:
       id_map["system"] = str(uuid.uuid4())

    # 2. Second Pass: Surgical Foreign Key Replacement

    # helper for resolving map
    def resolve(old_val):
        return id_map.get(old_val, old_val)

    for collection_name, items in data.items():
        if isinstance(items, list):
            for item in items:
                # Organizations
                if 'organization_id' in item and item['organization_id'] in id_map:
                    item['organization_id'] = id_map[item['organization_id']]

                if collection_name == 'workflows':
                    if 'steps' in item and isinstance(item['steps'], list):
                        item['steps'] = [resolve(s) for s in item['steps']]

                if collection_name == 'steps':
                    if 'config' in item:
                        config = item['config']
                        if 'matrix_id' in config:
                            config['matrix_id'] = resolve(config['matrix_id'])
                        if 'llm_prompts' in config and isinstance(config['llm_prompts'], list):
                            config['llm_prompts'] = [resolve(p) for p in config['llm_prompts']]

                    if 'inputs' in item:
                        # update $step_name references
                        new_inputs = {}
                        for k, v in item['inputs'].items():
                            # If key matches an old step id, update the key too
                            new_k = resolve(k)

                            new_v = v
                            if isinstance(v, str) and v.startswith('$'):
                                # e.g. $step_analyst
                                ref_id = v[1:]
                                if ref_id in step_id_map:
                                    new_v = f"${step_id_map[ref_id]}"
                                else:
                                    new_v = f"${resolve(ref_id)}" # generic fallback
                            new_inputs[new_k] = new_v
                        item['inputs'] = new_inputs

    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Surgical migration complete. Processed {len(id_map)} identities.")

if __name__ == "__main__":
    run_smart_migration()
