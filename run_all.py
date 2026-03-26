import json
import subprocess

print('Running seeder...')
subprocess.run(['python', 'backend_v2/seed/run_seed.py', 'local'], check=True)

print('Restoring mock execution...')
backup_file = 'data/backups/db_v2.json.20260319_185512.bak'
live_file = 'data/db_v2.json'

with open(backup_file, encoding='utf-8') as f:
    backup_data = json.load(f)

with open(live_file, encoding='utf-8') as f:
    live_data = json.load(f)

if 'executions' in backup_data and len(backup_data['executions']) > 0:
    live_data['executions'] = backup_data['executions']

    # We must also clear embedded render_blueprints from the restored execution
    # to force it to use the new seeded workflow blueprints
    for k, e in live_data['executions'].items():
        if 'render_blueprints' in e:
             del e['render_blueprints']

    with open(live_file, 'w', encoding='utf-8') as f:
        json.dump(live_data, f, indent=4, ensure_ascii=False)
    print('Restored execution securely.')

print('Running PDF generation...')
try:
    subprocess.run(['python', 'test_pdfs.py'], check=True)
    print('SUCCESS')
except Exception as e:
    print('Failed:', e)
