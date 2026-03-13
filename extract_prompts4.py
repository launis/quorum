import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

target_ids = [
    "block_taskjudge",
    "block_taskprofiler",
    "block_tasklogician",
    "block_taskfalsifier",
    "block_taskcausal",
    "block_taskanalyst"
]

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block["id"] in target_ids:
        print(f"========== {block['id']} ==========")
        print(block.get("system_prompt", "NONE"))
        print("\n" + "="*50 + "\n")
