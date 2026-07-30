import json

with open(r"c:\src\quorum\backend_v2\seed\seed_data.json", encoding="utf-8") as f:
    data = json.load(f)

# Scrub from top-level output_profiles
for profile in data.get("output_profiles", []):
    if "layouts" in profile:
        for layout in profile["layouts"]:
            if "extension_labels" in layout:
                del layout["extension_labels"]

with open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Successfully scrubbed extension_labels from top-level output_profiles!")
