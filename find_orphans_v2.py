import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

all_blocks = {block["id"]: block for block in data.get("prompt_blocks", [])}
referenced_blocks = set()

for workflow in data.get("workflows", []):
    for step in workflow.get("steps", []):
        if "prompt_blocks" in step:
            for pb in step["prompt_blocks"]:
                if isinstance(pb, str):
                    referenced_blocks.add(pb)

print(f"Total prompt blocks: {len(all_blocks)}")
print(f"Referenced directly by steps: {len(referenced_blocks)}")

orphans = set(all_blocks.keys()) - referenced_blocks
print("\nSome possible orphans (unreferenced by directly step.prompt_blocks):")
for orphan in list(orphans)[:20]:
    print(f"- {orphan}")

# Let's also check default_prompt_blocks if they exist globally
global_blocks = data.get("global_system_settings", {}).get("default_prompt_blocks", [])
print(f"\nGlobal Blocks: {global_blocks}")

for b in global_blocks:
    if isinstance(b, str):
        referenced_blocks.add(b)
        
remaining_orphans = set(all_blocks.keys()) - referenced_blocks
print(f"\nTotal real orphans approx: {len(remaining_orphans)}")
