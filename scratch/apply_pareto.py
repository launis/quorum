import json
import shutil
from pathlib import Path

seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
backup_file = seed_file.with_suffix('.json.bak')

TOP_5_ATOMS = {
    'tda_b620a45d39dc4f838b6ebc7cb1c37aed',
    'tda_5113d195df8e4eeb9d901af1c00a754d',
    'tda_453ddf8b14a442e988836098e3c7b55c',
    'tda_0f797e820117411d9934418a1d5d0a82',
    'tda_b899e72085ea4d488a6e6c22a34e2d75'
}

mod_count = 0
kept_count = 0

def walk_and_modify(node):
    global mod_count, kept_count
    if isinstance(node, dict):
        if 'high_entropy' in node and node['high_entropy'] is True:
            if node.get('tda_id') in TOP_5_ATOMS:
                kept_count += 1
            else:
                node['high_entropy'] = False
                mod_count += 1
        for k, v in node.items():
            walk_and_modify(v)
    elif isinstance(node, list):
        for item in node:
            walk_and_modify(item)

def apply_pareto():
    shutil.copy2(seed_file, backup_file)
    print(f"Backup created at: {backup_file}")

    with open(seed_file, encoding='utf-8') as f:
        data = json.load(f)

    walk_and_modify(data)

    with open(seed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print("Pareto correction applied.")
    print(f"Kept high_entropy=True for {kept_count} rules.")
    print(f"Set high_entropy=False for {mod_count} rules.")

if __name__ == "__main__":
    apply_pareto()
