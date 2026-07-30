import json

with open("scratch_seed_old.json", "r", encoding="utf-16") as f:
    data = json.load(f)

for item in data.get("output_profiles", []):
    if item.get("slug") == "holistic_audit":
        layouts = item.get("layouts", [])
        for i, l in enumerate(layouts):
            if 'compare' in l.get('preset_view', '') or 'matrix' in l.get('preset_view', ''):
                desc = l.get('description', {}).get('translations', {}).get('fi', '')
                print(f"[{i}] {l.get('preset_view')} | TargetBlocks: {l.get('target_blocks', [])} | Desc: {desc}")
