import json

path = r"c:\src\quorum\data\db_v2.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

steps = db.get("steps", {})
xai_step = steps.get("sp_192910b5f5a34c79")
if xai_step:
    print(f"XAI Reporter Step: {xai_step.get('label')}")
    print(f"Prompt Blocks: {xai_step.get('prompt_blocks')}")
else:
    print("XAI Reporter step not found in db_v2.json")
