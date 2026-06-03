import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== MUIHIN TOIMINTOIHIN LIITTYVÄT ASKELEET ===')
for step in data.get('steps', []):
    strat = step.get('model_strategy', 'PUUTTUU')
    name = step.get('name', {}).get('translations', {}).get('fi', step.get('id'))
    desc = step.get('description', {}).get('translations', {}).get('fi', '')
    
    # Ignore matrix steps already covered
    criteria = step.get('criteria_block_ids', [])
    if not criteria:
        print(f'Step: {name} (ID: {step.get("id")})')
        print(f' - Kuvaus: {desc}')
        print(f' - Strategia: {strat}')
        print(f' - Tyyppi: {step.get("type")}')
        print('---')

print('\n=== MUUT PROMPT BLOCKS (Ei-matriisit) ===')
for b in data.get('prompt_blocks', []):
    cat = b.get('category_id')
    if cat != 'matrix':
        name = b.get('label', {}).get('translations', {}).get('fi', b.get('id'))
        print(f'Lohko: {name} (Tyyppi: {cat})')
