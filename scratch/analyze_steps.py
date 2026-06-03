import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

matrix_names = {}
for b in data.get('prompt_blocks', []):
    if b.get('category_id') == 'matrix':
        label = b.get('label', {}).get('translations', {}).get('fi', b.get('id'))
        matrix_names[b['id']] = label

print("=== NYKYISET STRATEGIAT JA MUUTOSEHDOTUKSET ===")
for step in data.get('steps', []):
    strat = step.get('model_strategy', 'PUUTTUU')
    step_id = step.get('id')
    
    # Hae stepin matriisit
    criteria = step.get('criteria_block_ids', [])
    if not criteria:
        # Ehkä kyse on synteesistä?
        name = step.get('name', {}).get('translations', {}).get('fi', step_id)
        print(f"Step: {name} ({step_id})")
        print(f"  -> Nyt: {strat}")
        if 'Synteesi' in name or 'Synthesis' in name or strat == 'synthesis':
            print(f"  -> Suositus: deep (tai oletus, koska Synteesi vaatii aina parhaan mallin)")
        else:
            print(f"  -> Suositus: fast (jos vain datan parsimista)")
        print()
        continue

    for c in criteria:
        name = matrix_names.get(c, c)
        print(f"Matriisi: {name} (Step: {step_id})")
        print(f"  -> Nyt: {strat}")
        
        # Suosituslogiikka
        if any(kw in name for kw in ['Ohjeiden noudattaminen', 'Vastuullisuus', 'Avoimuus', 'Luottamusarvio']):
            print("  -> Suositus: fast (Pidetään nopeana/mekaanisena, eli tämä on OIKEIN)")
        else:
            print("  -> Suositus: deep / precise (Syvää päättelyä, MUUTETTAVA)")
        print()
