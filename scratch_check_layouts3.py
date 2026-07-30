import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data.get("output_profiles", []):
    if item.get("slug") == "holistic_audit":
        layouts = item.get("layouts", [])
        for i in range(7, len(layouts)):
            l = layouts[i]
            print(f"[{i}] {l.get('preset_view')} | TargetBlocks: {l.get('target_blocks', [])}")
            print(f"    Desc: {l.get('description', {}).get('translations', {}).get('fi')}")
