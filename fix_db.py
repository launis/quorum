import json

db_path = 'c:/src/quorum/data/db_v2.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

for w in db.get('workflows', {}).values():
    if w.get('id') == 'wf_d653170e174847559e08af42b938d826':
        bps = w.get('render_blueprints', {})
        metrics = bps.get('1d_metrics')
        if metrics:
            for comp in metrics.get('components', []):
                if comp.get('title') == 'Score 1':
                    comp['data_path'] = '$results.steprule_ec0bbf026f3a4952b35776114b971d38.blk_3c3b6a9b67bf41e88ed4b59524d6c6f3_normalized'
                elif comp.get('title') == 'Score 2':
                    comp['data_path'] = '$results.steprule_ec0bbf026f3a4952b35776114b971d38.blk_2878d1c8b5494180b1a5231466e2e0a9_normalized'

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2)
print("Done fixing database")
