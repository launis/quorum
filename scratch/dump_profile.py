import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

profiles = data.get('output_profiles', [])
target_profile = next((p for p in profiles if p.get('id') == 'prf_5d6e7f8091a2b3c4'), None)

if target_profile:
    print(json.dumps(target_profile, indent=2))
else:
    print("Profile not found")
