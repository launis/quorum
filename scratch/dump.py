import json
import os

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
out_path = r"c:\src\quorum\scratch\matrix_dump.json"
list_path = r"c:\src\quorum\scratch\matrix_list.txt"

os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

matrix_list = []
target_block = None

for block in data.get("prompt_blocks", []):
    if block.get("category_id") == "matrix":
        fi_label = block.get("label", {}).get("translations", {}).get("fi", "N/A")
        matrix_list.append(f"{block.get('id')} - {fi_label}")
        if block.get("id") == "blk_fb15f8dcf23f4865" or "Ohjeiden noudattaminen" in fi_label or "Arkistointistandardien" in fi_label:
            target_block = block

with open(list_path, "w", encoding="utf-8") as f:
    f.write("\n".join(matrix_list))

if target_block:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(target_block, f, indent=2, ensure_ascii=False)
    print(f"Target block {target_block['id']} dumped to scratch/matrix_dump.json")
else:
    print("Target block not found!")
