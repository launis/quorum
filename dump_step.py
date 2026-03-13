import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"
with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for wf in data.get("workflows", []):
    for step in wf.get("steps", []):
        if step["id"] == "step_judge":
            print(json.dumps(step, indent=2))
