import json

db = json.load(open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8'))
for pb in db.get('prompt_blocks', []):
    for scale in pb.get('scales', []):
        for claim in scale.get('claims', []):
            for tda in claim.get('tda_assertions', []):
                if 'concept_description' not in tda:
                    print(f"Missing concept_description in block {pb['id']} claim {claim['label']}")
                    print(tda)
