import json
import os
from datetime import datetime

seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
backup_dir = 'c:/src/quorum/backend_v2/seed/backups'

with open(seed_path, 'r', encoding='utf-8') as f:
    db = json.load(f)
    
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_file = f'{backup_dir}/seed_data_backup_normalization_hook_{timestamp}.json'
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"Backed up to {backup_file}")

# 1. Inject 'normalize_matrix_scores' into post_hooks for all steps
workflows = db.get('workflows', [])
for workflow in workflows:
    for step in workflow.get('steps', []):
        post_hooks = step.get('post_hooks')
        if post_hooks is None:
            step['post_hooks'] = ['normalize_matrix_scores']
        elif isinstance(post_hooks, list):
            if 'normalize_matrix_scores' not in post_hooks:
                post_hooks.append('normalize_matrix_scores')

# 2. Scanning for irregular scales to report to the user
irregular_scales = {}
def check_scales(items):
    for item in items:
        scales = item.get('scales')
        if scales and isinstance(scales, list) and len(scales) > 0:
            scores = []
            for s in scales:
                val = s.get('score')
                if val is not None:
                    scores.append(val)
            
            # Check if it deviates from the simple 1, 2, 3... pattern
            is_irregular = False
            for val in scores:
                if val not in [1, 2, 3, 4, 5, 1.0, 2.0, 3.0, 4.0, 5.0]:
                    is_irregular = True
                    break
            
            if is_irregular:
                irregular_scales[item.get('id')] = scores

check_scales(db.get('prompt_blocks', []))
check_scales(db.get('matrices', []))

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("Updated seed_data.json successfully with normalize_matrix_scores hook.")

print("--- IRREGULAR SCALES DETECTED ---")
if not irregular_scales:
    print("None found!")
for k, v in irregular_scales.items():
    print(f"{k}: {v}")
