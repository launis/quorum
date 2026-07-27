import json
data = json.load(open('backend_v2/seed/seed_data.json', encoding='utf-8'))
for p in data.get('output_profiles', []):
    blocks = p.get('content_blocks', [])
    if blocks:
        print(f"Profile {p['id']} has {len(blocks)} blocks:")
        print(json.dumps(blocks, indent=2))
