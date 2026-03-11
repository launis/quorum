import json
from pathlib import Path

seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
with open(seed_path, encoding='utf-8') as f:
    d = json.load(f)

blocks = {b['id']: b['description']['translations'].get('fi', b['id']) for b in d.get('prompt_blocks', [])}

print("=== PHASE 2 AUDIT ===")
for step_id in ['step_input_processing', 'step_guard', 'step_retrieval_agent']:
    s = next((st for st in d.get('steps', []) if st['id'] == step_id), None)
    if not s:
        print(f"NOT FOUND: {step_id}")
        continue
    
    prompts = s.get('prompt_blocks', [])
    print(f"\nSTEP: {step_id}")
    for idx, p in enumerate(prompts):
        desc = blocks.get(p, p).replace('\n', ' ')
        if len(desc) > 80: desc = desc[:80] + '...'
        print(f"  {idx+1}. {p} | {desc}")
