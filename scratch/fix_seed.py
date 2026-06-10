import json

seed_path = r'c:\src\quorum\backend_v2\seed\seed_data.json'

with open(seed_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for profile in data.get('output_profiles', []):
    if profile.get('strictness_level') == 50:
        print(f"Fixing profile {profile['id']} strictness from 50 to 85")
        profile['strictness_level'] = 85

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Seed data successfully patched.")
