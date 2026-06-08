import json
from pathlib import Path

seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def revert_type():
    with open(seed_file, encoding='utf-8') as f:
        data = json.load(f)

    blocks_updated = 0
    for block in data.get("prompt_blocks", []):
        if block.get("type") == "protocol":
            block["type"] = "instruction"
            blocks_updated += 1

    with open(seed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Reverted 'type' from 'protocol' back to 'instruction' in {blocks_updated} blocks.")

if __name__ == "__main__":
    revert_type()
