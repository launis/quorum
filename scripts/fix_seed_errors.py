import json

path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

profile = next(p for p in data["output_profiles"] if p["id"] == "prf_5d6e7f8091a2b3c4")

for layout in profile["layouts"]:
    # Fix target_blocks being None
    if "target_blocks" in layout and layout["target_blocks"] is None:
        layout["target_blocks"] = []

    # Fix allowed_exports having 'sdui'
    if "synthesis" in layout and layout["synthesis"]:
        if "allowed_exports" in layout["synthesis"]:
            layout["synthesis"]["allowed_exports"] = [
                exp for exp in layout["synthesis"]["allowed_exports"] if exp != "sdui"
            ]

    # Fix missing default_locale in title
    if "title" in layout and isinstance(layout["title"], dict):
        if "default_locale" not in layout["title"]:
            layout["title"]["default_locale"] = "fi"

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Fixed seed_data.json validation errors!")
