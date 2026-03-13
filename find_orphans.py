import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find all prompt blocks
all_blocks = {block["id"]: block for block in data.get("prompt_blocks", [])}

# Find all references in workflows
referenced_blocks = set()

def find_references(obj):
    if isinstance(obj, dict):
        if "prompt_blocks" in obj and isinstance(obj["prompt_blocks"], list):
            referenced_blocks.update(obj["prompt_blocks"])
        for k, v in obj.items():
            find_references(v)
    elif isinstance(obj, list):
        for item in obj:
            find_references(item)

for wf in data.get("workflows", []):
    find_references(wf)

print(f"Total prompt blocks: {len(all_blocks)}")
print(f"Referenced in workflows: {len(referenced_blocks)}")

orphans = set(all_blocks.keys()) - referenced_blocks
print("\nOrphan Prompt Blocks (not used in any workflow):")
for orphan in orphans:
    print(f"- {orphan}")
