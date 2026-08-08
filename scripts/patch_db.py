import json
import shutil

db_path = r'c:\src\quorum\data\db_v2.json'
backup_path = r'C:\src\quorum\backend_v2\seed\backups\db_v2.json.20260731_161717.bak'
seed_path = r'c:\src\quorum\backend_v2\seed\seed_data.json'

# Restore DB from backup
shutil.copy2(backup_path, db_path)

# Load DB and Seed Data
with open(db_path, encoding='utf-8') as f:
    db_data = json.load(f)
with open(seed_path, encoding='utf-8') as f:
    seed_data = json.load(f)

# Find new profile
new_profile = next(p for p in seed_data['output_profiles'] if p['id'] == 'prf_5d6e7f8091a2b3c4')

# Update profile in DB
# TinyDB stores tables under _default or named tables. Let's find where output_profiles is.
if 'output_profiles' in db_data:
    table = db_data['output_profiles']
    for key, item in table.items():
        if item.get('id') == 'prf_5d6e7f8091a2b3c4':
            table[key] = new_profile
            print("Updated profile in DB!")
            break

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(db_data, f, ensure_ascii=False)

print("DB restored and patched successfully!")
