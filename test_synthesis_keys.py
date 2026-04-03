import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for profile in data.get("output_profiles", []):
    if profile.get("id") == "prf_executive123":
        print(json.dumps(profile.get("synthesis"), indent=2))
        break
