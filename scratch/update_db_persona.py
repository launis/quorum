import json

path = r"c:\src\quorum\data\db_v2.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

prompt_blocks = db.get("prompt_blocks", {})
updated = 0

for key, block in prompt_blocks.items():
    block_str = json.dumps(block).lower()
    if "reporter" in block_str or "xai" in block_str:
        block["execution_persona"] = "XAI_REPORTER"
        updated += 1
        print(f"Updated block {key}")

if updated > 0:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Saved DB with {updated} updates.")
else:
    print("No blocks found to update.")
