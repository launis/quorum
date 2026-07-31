import json

path = r'C:\Users\risto\.gemini\antigravity-ide\brain\eb38cd8a-c615-4eea-b28a-3fe2ab84270f\scratch\15_layouts_full_enriched.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, l in enumerate(data):
    title = l.get('title', {})
    if title:
        title_fi = title.get('translations', {}).get('fi', '')
    else:
        title_fi = 'None'
    print(f"{i}: {l.get('preset_view')} - {title_fi} - {l.get('target_blocks')}")
