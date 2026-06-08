import json
from pathlib import Path

seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def refine_new_block():
    with open(seed_file, encoding='utf-8') as f:
        data = json.load(f)

    for block in data.get("prompt_blocks", []):
        if block.get("id") == "blk_573802341db9d68d":
            block["slug"] = "block_extraction_protocol_lightweight"
            block["description"]["translations"]["fi"] = "Kevyt, perustelut ohittava nopea poimintaprotokolla JSON-ulostulolle."
            block["description"]["translations"]["en"] = "Lightweight extraction protocol for direct JSON output without reasoning traces."
            break

    with open(seed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print("Refined slug and description for new protocol.")

if __name__ == "__main__":
    refine_new_block()
