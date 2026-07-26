import json
with open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    data = json.load(f)
for prof in data.get('output_profiles', []):
    print(prof['id'], prof.get('slug'))
    print("custom_preface:", prof.get('custom_preface'))
    print("tone_instruction:", prof.get('tone_instruction'))
