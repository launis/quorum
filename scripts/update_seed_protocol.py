import copy
import json
import os
from datetime import datetime

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
backup_dir = r"c:\src\quorum\backend_v2\seed\backups"

os.makedirs(backup_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(backup_dir, f"seed_data_{timestamp}.bak.json")

with open(seed_path, encoding="utf-8") as f:
    data = json.load(f)

# Save backup
with open(backup_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Backup saved to: {backup_path}")

original_data = copy.deepcopy(data)

# Find block blk_573802341db9d68c
block_found = False
for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_573802341db9d68c":
        block_found = True
        append_text = " SYMMETRICAL BURDEN OF PROOF: If the source text explicitly contradicts the claim, you MUST extract the contradicting text into the 'counter_quote' field and set the status to 'CONTESTED'. Never attempt to contest or fail a claim without providing physical counter-evidence."
        if append_text not in block["ai_description"]:
            block["ai_description"] += append_text
        break

if not block_found:
    print("Block not found!")
    exit(1)

# Write back
with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Modification complete. Validating changes...")

# Load both and compare
with open(backup_path, encoding="utf-8") as f:
    old_data = json.load(f)
with open(seed_path, encoding="utf-8") as f:
    new_data = json.load(f)

# Deep compare
diffs = 0
for k in old_data:
    if old_data[k] != new_data[k]:
        print(f"Key '{k}' changed.")
        diffs += 1
        if k == "prompt_blocks":
            for old_blk, new_blk in zip(old_data[k], new_data[k], strict=False):
                if old_blk != new_blk:
                    print(f"  -> Block {old_blk.get('id')} changed.")
                    for attr in old_blk:
                        if old_blk.get(attr) != new_blk.get(attr):
                            print(f"    - Attr '{attr}' changed.")
                            print(f"      OLD: {old_blk.get(attr)}")
                            print(f"      NEW: {new_blk.get(attr)}")

print("Validation finished.")
