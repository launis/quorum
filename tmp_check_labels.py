import json

db = json.load(open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8', errors='ignore'))
pb = db.get('prompt_blocks', [])

for m in pb:
    if m.get('type') in ('float', 'string', 'int'):
        scales = m.get('scales', [])
        labels = [s.get('name', {}).get('translations', {}).get('fi', '') for s in scales]
        print(f"{m.get('id')}: {m.get('scale_min')}-{m.get('scale_max')} | Labels: {labels}")
