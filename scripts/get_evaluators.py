import json

with open("c:/src/quorum/backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for b in data.get("prompt_blocks", []):
    if b.get("is_evaluative") and b.get("category_id") == "matrix":
        label = b.get("label", {}).get("translations", {}).get("fi", "N/A")
        print(f"- {label} ({b.get('slug')})")
