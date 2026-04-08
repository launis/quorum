import json
import os

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"

print(f"Reading {seed_path}...")
with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

all_extensions = [
    "citation",
    "falsification",
    "missing_context",
    "risk_flag",
    "coaching",
    "justification",
    "theory_link",
    "remediation_steps",
    "emotional_sentiment",
    "confidence"
]

updated_count = 0
for block in data.get("prompt_blocks", []):
    # Only update evaluative blocks or blocks that make sense
    if block.get("is_evaluative", True):
        block["output_extensions"] = all_extensions
        updated_count += 1

print(f"Updating {updated_count} PromptBlocks with full XAI output_extensions...")

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Running seed to flush changes into db_v2.json...")
os.system(r"uv run python backend_v2\seed\run_seed.py")

print("All done! Try running the execution again in the UI.")
