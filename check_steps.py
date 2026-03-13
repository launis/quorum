import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"
with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for step in data.get("steps", []):
    if step["id"] in ["step_judge", "step_causal_analyst", "step_falsifier", "step_analyst"]:
        print(f"Step: {step['id']} -> Prompts: {step.get('prompt_blocks', [])}")
