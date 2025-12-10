import json
try:
    with open('data/seed_data.json', encoding='utf-8') as f:
        d = json.load(f)
    print(f"Components: {len(d.get('components', []))}")
    print(f"Steps: {len(d.get('steps', []))}")
    print(f"Workflows: {len(d.get('workflows', []))}")
except Exception as e:
    print(f"Error: {e}")
