import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

target_ids = [
    "matrix_judge",
    "matrix_bloom",
    "matrix_toulmin",
    "matrix_profiler",
    "matrix_causal_analyst"
]

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block["id"] in target_ids:
        print(f"========== {block['id']} ==========")
        print("SYSTEM PROMPT:")
        print(block.get("system_prompt", "NONE"))
        print("\nSCHEMA CONTEXT:")
        print(block.get("schema_context", "NONE"))
        print("\n" + "="*50 + "\n")
