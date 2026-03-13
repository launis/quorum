import json
import os
from datetime import datetime

file_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
backup_path = f'c:/src/quorum/backend_v2/seed/backups/seed_data_backup_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'

with open(file_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

# Backup first
os.makedirs(os.path.dirname(backup_path), exist_ok=True)
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# Patching
pb = db.get('prompt_blocks', [])
changes = []
for m in pb:
    if m.get('type') in ('float', 'int'):
        scales = m.get('scales', [])
        n = len(scales)
        if n > 0:
            if m.get('id') == 'block_taskguard':
                continue # leave it as is if it's correct
            old_min = m.get('scale_min')
            old_max = m.get('scale_max')
            # For Bloom and Toulmin it might be 0 to 6 in requirements, but let's use 1 to length
            # Let's check what the user wants. Usually 1 to N is safest, except if specified otherwise.
            # Bloom has 6 labels. So 1 to 6. Toulmin 5 labels -> 1 to 5.
            m['scale_min'] = 1
            m['scale_max'] = n
            if old_min != 1 or old_max != n:
                changes.append(f"{m.get('id')}: {old_min}-{old_max} -> 1-{n}")

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Patched the following scales:")
for c in changes:
    print(c)
