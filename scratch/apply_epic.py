import json
import shutil
from pathlib import Path

seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
backup_file = seed_file.with_suffix('.json.bak_epic')

OLD_ID = "blk_573802341db9d68c"
NEW_ID = "blk_lightweight_extract_01"

def apply_epic():
    shutil.copy2(seed_file, backup_file)
    print(f"Backup created at: {backup_file}")

    with open(seed_file, encoding='utf-8') as f:
        data = json.load(f)

    # 1. Create the new protocol block
    new_block = None
    workflows = data.get("workflows", [])
    for block in data.get("prompt_blocks", []):
        if block.get("id") == OLD_ID:
            new_block = json.loads(json.dumps(block))  # deep copy
            new_block["id"] = NEW_ID
            new_block["title"] = "Kevyt JSON-uutto (Ei perusteluja)"
            new_block["ai_description"] = "CRITICAL DIRECTIVE: Perform a lightweight, silent structural extraction. Do not generate 'thought' blocks or exceptions audits. Output ONLY the JSON object matching the requested schema."
            break

    if new_block:
        data["prompt_blocks"].append(new_block)
        print(f"Created new block {NEW_ID}")
    else:
        print(f"Failed to find {OLD_ID}")
        return

    # 2. Update steps
    steps_updated = 0
    for step in data.get("steps", []):
        if step.get("extraction_protocol_block_id") == OLD_ID:
            step["extraction_protocol_block_id"] = NEW_ID
            steps_updated += 1

    print(f"Updated {steps_updated} steps to use {NEW_ID}")

    with open(seed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print("Epic Execution Optimization applied successfully.")

if __name__ == "__main__":
    apply_epic()
