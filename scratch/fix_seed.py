import json
from pathlib import Path

seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

OLD_INVALID_ID = "blk_lightweight_extract_01"
NEW_VALID_ID = "blk_573802341db9d68d"

def fix_seed():
    with open(seed_file, encoding='utf-8') as f:
        data = json.load(f)

    # 1. Fix the prompt block
    fixed = False
    for block in data.get("prompt_blocks", []):
        if block.get("id") == OLD_INVALID_ID:
            block["id"] = NEW_VALID_ID
            if "title" in block:
                del block["title"]
            block["label"]["translations"]["fi"] = "Kevyt JSON-uutto (Ei perusteluja)"
            block["label"]["translations"]["en"] = "Lightweight JSON Extraction (No Reasoning)"
            fixed = True
            break

    if not fixed:
        print(f"Failed to find {OLD_INVALID_ID} in prompt_blocks")
        return

    # 2. Update steps
    steps_updated = 0
    for step in data.get("steps", []):
        if step.get("extraction_protocol_block_id") == OLD_INVALID_ID:
            step["extraction_protocol_block_id"] = NEW_VALID_ID
            steps_updated += 1

    print(f"Updated {steps_updated} steps to use {NEW_VALID_ID}")

    with open(seed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print("Pydantic Validation errors fixed.")

if __name__ == "__main__":
    fix_seed()
