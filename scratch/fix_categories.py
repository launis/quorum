import json
from pathlib import Path

seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def fix_categories():
    with open(seed_file, encoding='utf-8') as f:
        data = json.load(f)

    blocks_updated = 0
    for block in data.get("prompt_blocks", []):
        if block.get("category_id") == "instruction":
            block["category_id"] = "protocol"
            blocks_updated += 1
        if block.get("type") == "instruction":
            block["type"] = "protocol"

    with open(seed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Fixed category 'instruction' -> 'protocol' in {blocks_updated} blocks.")

if __name__ == "__main__":
    fix_categories()
