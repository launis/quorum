import json
from pathlib import Path

seed_file = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
with open(seed_file, encoding="utf-8") as f:
    data = json.load(f)

# The correct strategy mapping for the steps:
step_targets = {
    "sp_bd0b3054fe664960": "strict",  # Causal Analyst
    "sp_6a45d484ad5b497c": "strict",  # Profiler
    "sp_7f9649114d2344dc": "strict",  # Perperformitivity Detector
    "sp_76eedbc020274f66": "strict",  # Fact Checker
    "sp_192910b5f5a34c79": "deep",  # XAI Reporter
}

# The exclusive prompt blocks that should trigger lightweight (1x) protocol for these steps
block_targets = [
    "blk_c5804a9143c34cb1",
    "blk_43e297666d3b4359",  # Causal
    "blk_c3bc5f3eb8e74110",
    "blk_9c0c7c46568648c4",  # Profiler
    "blk_b4912f9ff3a24b31",
    "blk_fb15f8dcf23f4865",  # Perperformitivity
    "blk_22e3598e06414409",
    "blk_033180746a954415",  # Fact Checker
    "blk_6b8c766185294f7e",  # XAI Reporter
]

steps_modified = 0
blocks_modified = 0

print("--- UPDATING STEPS ---")
for step in data.get("steps", []):
    sid = step.get("id")

    # Clean up my previous mistaken fields if they exist
    if "model_type" in step:
        del step["model_type"]
    if "evaluation_run_count" in step:
        del step["evaluation_run_count"]

    if sid in step_targets:
        old_strategy = step.get("model_strategy")
        new_strategy = step_targets[sid]
        if old_strategy != new_strategy:
            step["model_strategy"] = new_strategy
            print(f"Step {sid} updated: model_strategy {old_strategy} -> {new_strategy}")
            steps_modified += 1
        else:
            print(f"Step {sid} already has correct model_strategy: {new_strategy}")

print("\n--- UPDATING PROMPT BLOCKS ---")
for block in data.get("prompt_blocks", []):
    bid = block.get("id")
    if bid in block_targets:
        old_val = block.get("is_lightweight_protocol", False)
        if not old_val:
            block["is_lightweight_protocol"] = True
            print(f"Block {bid} updated: is_lightweight_protocol False -> True")
            blocks_modified += 1
        else:
            print(f"Block {bid} already has is_lightweight_protocol=True")

print(f"\nSteps modified: {steps_modified}")
print(f"Blocks modified: {blocks_modified}")

with open(seed_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("\nSuccess: seed_data.json updated.")
