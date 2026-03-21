import json

def get_missing_translations():
    with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        data = json.load(f)
        
    missing = set()
    def walk(d):
        if isinstance(d, dict):
            if 'fi' in d and 'en' in d and 'Auto-filled' in d['en']:
                missing.add(d['fi'])
            for v in d.values():
                walk(v)
        elif isinstance(d, list):
            for i in d:
                walk(i)
                
    walk(data)
    for m in missing:
        print(f'"{m}": "",')

get_missing_translations()
