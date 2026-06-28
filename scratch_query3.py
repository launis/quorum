import json

with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

wf = list(db.get('workflows', {}).values())[0]
blueprint = wf.get('steps', [])[0].get('task_blueprint', {})
print(blueprint.keys())
print('Matrices count:', len(blueprint.get('matrices', [])))
if blueprint.get('matrices'):
    print('Matrix keys:', blueprint['matrices'][0].keys())
    print('Row keys:', blueprint['matrices'][0].get('rows', [])[0].keys())
