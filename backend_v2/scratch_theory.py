import json

with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for pb in db.get('prompt_blocks', []):
    name = pb.get('label', {}).get('translations', {}).get('fi', '')
    theory = pb.get('theory_grounding')
    print(f"{name}: theory={theory is not None}")
    if theory:
        print(f"  -> {theory.get('source_type')}: {theory.get('reference_id')}")
