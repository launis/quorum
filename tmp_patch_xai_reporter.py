import json

seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
with open(seed_path, 'r', encoding='utf-8') as f:
    db = json.load(f)
    
score_map = {0: 1, 50: 2, 100: 3}

patched = False
for list_name in ['prompt_blocks', 'matrices']:
    for item in db.get(list_name, []):
        if item.get('id') == 'matrix_xai_reporter':
            scales = item.get('scales', [])
            for scale in scales:
                old_score = scale.get('score')
                if old_score in score_map:
                    scale['score'] = score_map[old_score]
                    patched = True

if patched:
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("Updated matrix_xai_reporter successfully in seed_data.json.")
else:
    print("Could not find or patch matrix_xai_reporter.")
