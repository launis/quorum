import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Profiles:", type(data.get("output_profiles", [])))
if len(data.get("output_profiles", [])) > 0:
    profile = data["output_profiles"][0]
    print("Keys:", profile.keys())
