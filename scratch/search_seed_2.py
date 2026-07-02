import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for profile in data.get("output_profiles", []):
    print(f"--- OutputProfile: {profile.get('name')} ---")
    for block in profile.get("blocks", []):
        print(f"Slug: {block.get('slug')}, Type: {block.get('block_type')}")
        if block.get('block_type') == 'SYNTHESIS':
            print(f"  Synthesis prompt: {block.get('synthesis_prompt')}")
