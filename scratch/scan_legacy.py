import json

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    needs_refactor = []

    for cat in ['evaluations', 'matrices']:
        for eval_obj in data.get(cat, []):
            matrix_name = eval_obj.get('name', {}).get('translations', {}).get('fi', eval_obj.get('id'))

            for claim in eval_obj.get('claims', []):
                claim_name = claim.get('label', {}).get('translations', {}).get('fi', 'Unknown Claim')

                for tda in claim.get('tda_assertions', []):
                    desc = tda.get('concept_description', '')
                    if '<disambiguation>' in desc or '<syntactic_constraint>' in desc or 'EXCLUSION:' in desc:
                        needs_refactor.append({
                            'matrix': matrix_name,
                            'claim': claim_name,
                            'tda_id': tda.get('tda_id', 'Unknown'),
                            'desc_preview': desc[:100] + '...'
                        })

    print(f"Found {len(needs_refactor)} assertions that need refactoring:")
    for item in needs_refactor:
        print(f"- Matrix: {item['matrix']} | Claim: {item['claim']} | TDA: {item['tda_id']}")

except Exception as e:
    print(f"Error: {e}")
