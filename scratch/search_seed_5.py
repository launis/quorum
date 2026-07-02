import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for profile in data.get("output_profiles", []):
    print(f"--- OutputProfile: {profile.get('name')} ---")
    synthesis = profile.get("synthesis", [])
    print("Synthesis config:")
    print(json.dumps(synthesis, indent=2))
