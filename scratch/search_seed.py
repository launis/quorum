import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if "executive" in block.get("name", "").lower() or "tiivistelm" in block.get("name", "").lower() or "summary" in block.get("name", "").lower() or "koonti" in block.get("name", "").lower():
        print(f"--- PromptBlock: {block.get('name')} ---")
        print(block.get("ai_description"))
        print(block.get("system_prompt"))
        print("-" * 40)

for profile in data.get("output_profiles", []):
    print(f"--- OutputProfile: {profile.get('name')} ---")
    for block in profile.get("blocks", []):
        if "synthesis" in block.get("block_type", "").lower() or "executive" in block.get("slug", "").lower():
            print(block)
