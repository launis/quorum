import json

with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

prompt_blocks = {pb['id']: pb for pb in data.get('prompt_blocks', [])}

print("--- Root Output Profiles ---")
for profile in data.get('output_profiles', []):
    print(f"Profile: {profile.get('slug')} - {profile.get('id')}")
    for i, layout in enumerate(profile.get('layouts', [])):
        if layout.get('preset_view') == '1d_metrics':
            print(f"  Layout {i}: preset_view={layout.get('preset_view')}")
            tb = layout.get('target_blocks', [])
            if tb and tb[0] in prompt_blocks:
                pb = prompt_blocks[tb[0]]
                matrix_name = pb.get('label', {}).get('translations', {}).get('fi', 'Unknown')
                print(f"    matrix name: {matrix_name}")
            else:
                print(f"    matrix name: Unknown")
            if 'title' in layout and layout['title']:
                fi_title = layout['title'].get('translations', {}).get('fi', '')
                print(f"    current title (FI): {fi_title}")
