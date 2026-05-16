import json

path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

steps = db.get("steps", [])
for s in steps:
    if s.get("id") == "sp_192910b5f5a34c79":
        print(f"Step sp_192910b5f5a34c79 Prompt Blocks: {s.get('prompt_blocks')}")
