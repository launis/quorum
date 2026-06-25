import json

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))
blocks = d.get("prompt_blocks", [])

block_light_map = {}
for b in blocks:
    block_light_map[b["id"]] = b.get("is_lightweight_protocol", False)

steps = d.get("steps", [])
print(f"\n=== WORKFLOW STEPS ===")
for s in steps:
    strategy = s.get("model_strategy", "?")  # It's model_strategy, not llm_strategy in the JSON
    name = s.get("slug", s.get("id", "?"))
    
    criteria_ids = s.get("criteria_block_ids", [])
    is_light = any(block_light_map.get(cid, False) for cid in criteria_ids)
    
    print(f"  Step '{name}': strategy={strategy}, is_lightweight={is_light}, runs={'1 (STANDARD)' if is_light else '3 (ENSEMBLE)'}")
