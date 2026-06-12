import json

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    legacy_items = []

    for cat in ['evaluations', 'matrices']:
        for matrix in data.get(cat, []):
            name_obj = matrix.get('name', matrix.get('label', {}))
            if isinstance(name_obj, dict):
                trans = name_obj.get('translations', name_obj)
                matrix_name = trans.get('fi', trans.get('en', matrix['id']))
            else:
                matrix_name = name_obj if isinstance(name_obj, str) else matrix['id']

            for claim in matrix.get('claims', []):
                clab_obj = claim.get('label', {})
                if isinstance(clab_obj, dict):
                    ctrans = clab_obj.get('translations', clab_obj)
                    claim_name = ctrans.get('fi', ctrans.get('en', 'Unknown Claim'))
                else:
                    claim_name = clab_obj

                for tda in claim.get('tda_assertions', []):
                    desc = tda.get('concept_description', '')
                    if '<disambiguation>' in desc or 'EXCLUSION:' in desc:
                        legacy_items.append({
                            'matrix': matrix_name,
                            'claim': claim_name,
                            'tda_id': tda.get('tda_id', 'Unknown'),
                            'desc': desc
                        })

    print(f"Found {len(legacy_items)} assertions:")
    for item in legacy_items:
        print(f"Matrix: {item['matrix']} | Claim: {item['claim']}")

except Exception as e:
    print(f"Error: {e}")
