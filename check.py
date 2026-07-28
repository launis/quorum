import json
d = json.load(open('c:/src/quorum/backend_v2/seed/backups/db_v2.json.20260728_162132.bak', encoding='utf-8'))
execs = d.get('executions')
exe = None
if isinstance(execs, dict): exe = execs.get('exe_986b6e856c494e708dc1410e0a4d309a')
elif isinstance(execs, list): exe = next((e for e in execs if e.get('id') == 'exe_986b6e856c494e708dc1410e0a4d309a'), None)

if exe:
    for p_id, p_data in exe.get('profile_syntheses', {}).items():
        print(f'Profile {p_id} xai_highlights length:', len(p_data.get('xai_highlights', [])))
        print(p_data.get('xai_highlights'))
else:
    print('Execution not found in dict or list')
