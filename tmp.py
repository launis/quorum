import json

with open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

wf = next(w for w in data['workflows'] if w['slug'] == 'kokonaisvaltainen_auditointi')
step_ids = wf['steps']
found_steps = [s for s in data['steps'] if s['id'] in step_ids]
blocks = data.get('prompt_blocks', [])

text = ''
for s in found_steps:
    text += f"\nStep {s['name']['translations']['fi']} ({s['id']}):\n"
    for pb_id in s['prompt_blocks']:
        pb = next((b for b in blocks if b['id'] == pb_id), None)
        if pb:
            text += f"  - {pb['label']['translations']['fi']} ({pb['id']})\n"
        else:
            text += f"  - Unknown block {pb_id}\n"

print(text)
