import json
with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

for b in data['prompt_blocks']:
    if b.get('allow_decimals') or b.get('scales'):
        fi_label = b.get('label', {}).get('translations', {}).get('fi', b['id'])
        print(f"{b['id']}: {fi_label}")
