import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
layouts = next(i for i in data['output_profiles'] if i['slug'] == 'holistic_audit')['layouts']
for i, l in enumerate(layouts):
    desc = l.get('description', {}).get('translations', {}).get('fi', '')
    title = l.get('title', {}).get('translations', {}).get('fi', '')
    if 'Kryptisten' in desc or 'Kryptisten' in title:
        print(f"[{i}] {l.get('preset_view')} | Title: {title} | Desc: {desc}")
