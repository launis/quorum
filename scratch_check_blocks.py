import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

pb = data.get('prompt_blocks', [])
ids = [b['id'] for b in pb]
for target in ['blk_6b8c766185294f7e', 'blk_f6e286f050c94d60']:
    print(f"{target} exists: {target in ids}")
