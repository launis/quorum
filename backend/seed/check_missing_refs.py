import json

SEED_PATH = r"backend/seed/seed_data.json"

try:
    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    defined_ids = set()
    referenced_ids = set()

    # 1. Collect Defined IDs
    # data is a list of objects in the new format (or dict with keys if not fully flattened yet?)
    # Based on previous `view_file`, it's a list.

    items = data if isinstance(data, list) else []
    if isinstance(data, dict):
         # If it's a dict (e.g. legacy format or wrapper), extract lists
         for key in ["instructions", "mandates", "rules", "tasks", "steps", "workflows", "components"]:
             items.extend(data.get(key, []))

    for item in items:
        if isinstance(item, dict) and 'id' in item:
            defined_ids.add(item['id'])

    # 2. Collect Referenced IDs
    for item in items:
        # Check Step Configs
        if item.get("config"):
            prompts = item["config"].get("llm_prompts", [])
            for p in prompts:
                referenced_ids.add(p)

    # 3. Find Missing
    missing = referenced_ids - defined_ids

    print("-" * 30)
    print(f"Defined IDs: {len(defined_ids)}")
    print(f"Referenced IDs: {len(referenced_ids)}")
    print("-" * 30)

    if missing:
        print("MISSING REFERENCES (Defined in prompts but not found in ID list):")
        for m in sorted(list(missing)):
             print(f" - {m}")
    else:
        print("SUCCESS: All referenced prompts are defined.")

except Exception as e:
    print(f"Error: {e}")
