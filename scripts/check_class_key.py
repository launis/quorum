
import json
import os

SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"
DB_PATH = r"c:\src\quorum\data\db.json"

def check_json_for_class_key(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    print(f"Checking {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data.get("components", []) if isinstance(data, dict) else []
    if isinstance(components, dict):
        components = list(components.values())

    count = 0
    for c in components:
        if "class" in c:
            count += 1
            if count <= 3:
                print(f"Found 'class' in component {c.get('id')}: {c['class']}")
    
    print(f"Total components with 'class': {count}")

check_json_for_class_key(SEED_PATH)
check_json_for_class_key(DB_PATH)
