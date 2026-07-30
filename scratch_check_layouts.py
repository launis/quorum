import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data.get("output_profiles", []):
    if item.get("slug") == "holistic_audit":
        for i, l in enumerate(item.get("layouts", [])):
            if 'compare' in l.get('preset_view', '') or 'matrix' in l.get('preset_view', ''):
                desc = l.get('description', {}).get('translations', {}).get('fi', '')
                axes = l.get('target_blocks', [])
                print(f"{i}: {l.get('preset_view')} - {desc}")
                print(f"   Target Blocks: {axes}")
                synth = l.get('synthesis', {})
                if synth:
                    preamble = synth.get('preamble_text', {}).get('translations', {}).get('fi', '')
                    print(f"   Synthesis: YES (Preamble: {preamble})")
                else:
                    print(f"   Synthesis: NO")
