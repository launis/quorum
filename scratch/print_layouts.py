import json
data = json.load(open('backend_v2/seed/seed_data.json', encoding='utf-8'))
for i, l in enumerate(data['output_profiles'][0]['layouts']):
    print(f"{i}: {l['preset_view']} - {l.get('title')}")
