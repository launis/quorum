import json

with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for wf in data.get('workflows', []):
    profiles = wf.get('output_profiles', {})
    for p_key, p_val in profiles.items():
        print(f"Workflow: {wf.get('slug')}, Profile: {p_key}")
        for i, layout in enumerate(p_val.get('layouts', [])):
            print(f"  Layout {i}: preset_view={layout.get('preset_view')}")
            if 'synthesis' in layout and layout['synthesis']:
                synth = layout['synthesis']
                print(f"    synthesis length: {synth.get('length_constraint')}")
                system_prompt = synth.get('system_prompt', '')
                print(f"    system_prompt preview: {system_prompt[:60]}...")
            if 'title' in layout and layout['title']:
                fi_title = layout['title'].get('translations', {}).get('fi', '')
                print(f"    title (FI): {fi_title}")
