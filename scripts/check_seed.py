import json

db = json.load(open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8'))
for pb in db['prompt_blocks']:
    if 'scales' in pb:
        print("Block ID:", pb['id'])
        tda = pb['scales'][0]['claims'][0]['tda_assertions'][0]
        print("Keys:", list(tda.keys()))
        if 'concept_description' in tda:
            print("concept_description:", tda['concept_description'])
        break
