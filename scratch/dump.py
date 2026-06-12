import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
    d = json.load(f)

for cat in d:
    if isinstance(d[cat], list):
        for item in d[cat]:
            if isinstance(item, dict) and item.get('id') == 'blk_109dab5b6b3f403a':
                print(f"Found in {cat}:")
                print(json.dumps(item, indent=2, ensure_ascii=False))
