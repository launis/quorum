import json
import os

path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

prompt_blocks = db.get("prompt_blocks", [])
updated = 0

for block in prompt_blocks:
    block_str = json.dumps(block).lower()
    # Check for XAI Reporter
    if "reporter" in block_str or "xai" in block_str:
        block["execution_persona"] = "XAI_REPORTER"
        updated += 1
        print(f"Updated XAI_REPORTER block: {block.get('id')}")
    # Check for Coach
    elif "coach" in block_str:
        block["execution_persona"] = "COACH"
        updated += 1
        print(f"Updated COACH block: {block.get('id')}")

if updated > 0:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Saved seed_data.json with {updated} updates.")
else:
    print("No blocks found to update.")
