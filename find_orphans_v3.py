import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    text = f.read()

data = json.loads(text)
all_blocks = {block["id"]: block for block in data.get("prompt_blocks", [])}

orphans = []
for block_id in all_blocks:
    # Check if the block ID appears anywhere else in the file verbatim, avoiding its own definition definition
    count = text.count(f'"{block_id}"')
    if count <= 1:
        orphans.append(block_id)

print("\nActual Orphans (0 references anywhere else in the file):")
for orphan in orphans:
    print(f"- {orphan}")
