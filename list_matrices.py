import json

path = r'c:\src\quorum\backend_v2\seed\seed_data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for b in data['prompt_blocks']:
    if b.get('slug', '').startswith('matrix_'):
        title = b.get('title', {}).get('translations', {}).get('fi', '')
        name = b.get('name', {}).get('translations', {}).get('fi', '')
        if not title:
            title = name
        print(f"{b['id']}: {b['slug']} - {title}")
