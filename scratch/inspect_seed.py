import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Keys at root level:")
print(list(data.keys()))

if 'output_profiles' in data:
    profiles = data['output_profiles']
    print("\nOutput profiles:")
    for profile in profiles:
        print(f"ID: {profile.get('id')}")
        print(f"Type: {profile.get('type')}")
        print(f"Name: {profile.get('name')}")
