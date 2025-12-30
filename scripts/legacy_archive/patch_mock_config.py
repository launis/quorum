
import json
import os

db_path = r'c:\Users\risto\OneDrive\quorum\data\db_mock.json'

if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

# Find the config component
comps = db.get('components', {})
target_id = "COACH_OUTPUT_CONFIG"
target_key = None

for k, v in comps.items():
    if v.get('id') == target_id:
        target_key = k
        break

if target_key:
    comp = comps[target_key]
    content = comp.get('content', [])
    if "oppimispolku_viikko" in content:
        print(f"Removing oppimispolku_viikko from {target_id}")
        content.remove("oppimispolku_viikko")
        comp['content'] = content
        comps[target_key] = comp
        db['components'] = comps
        
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4)
        print("Successfully patched db_mock.json")
    else:
        print("oppimispolku_viikko not found in content list.")
else:
    print(f"Component {target_id} not found.")
