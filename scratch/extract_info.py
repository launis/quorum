import json
import os

with open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

blocks = {b['id']: b for b in data.get('prompt_blocks', [])}

for prof in data.get('output_profiles', []):
    for i, layout in enumerate(prof.get('layouts', [])):
        if layout.get('preset_view') in ['1d_metrics', '2d_compare']:
            title = layout.get('title')
            desc = layout.get('description')
            targets = layout.get('target_blocks', [])
            print(f"Layout {i} ({layout.get('preset_view')}): targets={targets}")
            print(f"  Title: {title}")
            print(f"  Desc: {desc}")
            for t in targets:
                b = blocks.get(t, {})
                print(f"    Block {t} name: {b.get('name')}")
                print(f"    Block {t} desc: {b.get('description')}")
