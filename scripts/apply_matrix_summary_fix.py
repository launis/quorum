import json

seed_path = r'c:\src\quorum\backend_v2\seed\seed_data.json'
db_path = r'c:\src\quorum\data\db_v2.json'

with open(seed_path, 'r', encoding='utf-8') as f:
    seed_data = json.load(f)
    
matrices = [b['id'] for b in seed_data['prompt_blocks'] if b.get('category_id') == 'matrix']

profile = next(p for p in seed_data['output_profiles'] if p['id'] == 'prf_5d6e7f8091a2b3c4')

# Find and remove matrix_summary
summary_layout = None
for i, l in enumerate(profile['layouts']):
    if l.get('preset_view') == 'matrix_summary':
        summary_layout = profile['layouts'].pop(i)
        break

if summary_layout:
    # Update target_blocks
    summary_layout['target_blocks'] = matrices
    
    # Ensure columns
    summary_layout['matrix_visible_columns'] = ["label", "distribution", "row_explanation", "score"]
    
    # Insert at index 1
    profile['layouts'].insert(1, summary_layout)

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(seed_data, f, indent=4, ensure_ascii=False)

# Now update the DB directly
with open(db_path, 'r', encoding='utf-8') as f:
    db_data = json.load(f)

if 'output_profiles' in db_data:
    for key, item in db_data['output_profiles'].items():
        if item.get('id') == 'prf_5d6e7f8091a2b3c4':
            db_data['output_profiles'][key] = profile
            break

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(db_data, f, ensure_ascii=False)

print("matrix_summary moved to index 1 and updated with all matrices in both seed_data.json and db_v2.json!")
