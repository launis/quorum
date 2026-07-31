import json

path = r'c:\src\quorum\backend_v2\seed\seed_data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

profile = next(p for p in data['output_profiles'] if p['id'] == 'prf_5d6e7f8091a2b3c4')

for i, l in enumerate(profile['layouts']):
    title = l.get('title', {})
    if title:
        title_fi = title.get('translations', {}).get('fi', '')
    else:
        title_fi = 'None'
    print(f"{i}: {title_fi} - {l.get('target_blocks')}")
