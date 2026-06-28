import json

with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

wf = list(db.get('workflows', {}).values())[0]
print(wf.get('steps', [])[0].keys())
