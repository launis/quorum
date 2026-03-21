import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for b in data.get("prompt_blocks", []):
    if b.get("category_id") == "matrix":
        print(b["id"], b.get("slug"), b.get("label", {}).get("translations", {}).get("en"))
