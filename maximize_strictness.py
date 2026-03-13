import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# The "strictness_level" property currently typically ranges from 1 to 100 or is 50 by default.
# The user wants "the strictest possible" evaluation.

modified_count = 0
for block in data.get("prompt_blocks", []):
    if block.get("type") in ["instruction", "matrix"]:
        if "strictness_level" in block:
            old_val = block["strictness_level"]
            block["strictness_level"] = 100
            if old_val != 100:
                print(f"Set strictness_level of {block['id']} from {old_val} to 100")
                modified_count += 1
        else:
            block["strictness_level"] = 100
            print(f"Added strictness_level 100 to {block['id']}")
            modified_count += 1

print(f"\n======================================")
print(f"Total blocks hardened to max strictness: {modified_count}")

with open(SEED_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nSUCCESS: seed_data_modified.json written with maximum strictness.")
