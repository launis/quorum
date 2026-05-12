import json
with open('c:/src/quorum/backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
block = next((b for b in data['prompt_blocks'] if b['id'] == 'blk_f921c7c0989b47e8'), None)
for s in block['scales']:
    print(f"SCORE {s['score']}:")
    for c in s['claims']:
        print(f"  - {c['label']['translations']['fi']}")
