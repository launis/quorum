import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

target_ids = [
    "block_taskjudge",
    "block_taskcausal",
    "block_taskfalsifier"
]

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block["id"] in target_ids:
        print(f"========== {block['id']} ==========")
        print(json.dumps(block, indent=2))
        print("\n" + "="*50 + "\n")
