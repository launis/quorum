import json

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))
blocks = {b["id"]: b for b in d.get("prompt_blocks", [])}

# Find cognitive friction blocks
cf_ids = {"blk_f84dc457f6184358", "blk_ad6f491a05ec4386"}
lw_ids = {b["id"] for b in d.get("prompt_blocks", []) if b.get("is_lightweight_protocol")}

print("=== COGNITIVE FRICTION BLOCKS ===")
for bid in cf_ids:
    b = blocks.get(bid)
    if b:
        print(f"  {bid}: {b.get('slug')} | is_lightweight_protocol={b.get('is_lightweight_protocol', False)}")

print(f"\n=== LIGHTWEIGHT BLOCKS ===")
for bid in sorted(lw_ids):
    b = blocks.get(bid)
    print(f"  {bid}: {b.get('slug')}")

# Critical: which steps have BOTH cognitive friction AND lightweight?
steps = d.get("steps", [])
print(f"\n=== STEPS WITH COGNITIVE FRICTION BLOCKS ===")
for s in steps:
    name = s.get("slug", s.get("id", "?"))
    strategy = s.get("model_strategy", "?")
    criteria_ids = set(s.get("criteria_block_ids", []))
    
    has_cf = bool(criteria_ids & cf_ids)
    has_lw = any(blocks.get(cid, {}).get("is_lightweight_protocol", False) for cid in criteria_ids)
    
    if has_cf:
        runs = "1 (LIGHTWEIGHT)" if has_lw else "3 (ENSEMBLE)"
        conflict = " *** CONFLICT! ***" if has_cf and has_lw else ""
        print(f"  Step: {name} | strategy={strategy} | runs={runs}{conflict}")
        for cid in criteria_ids:
            b = blocks.get(cid, {})
            is_lw = b.get("is_lightweight_protocol", False)
            cat = b.get("category_id", "?")
            slug = b.get("slug", "?")
            marker = " [LIGHTWEIGHT]" if is_lw else ""
            marker2 = " [COG_FRICTION]" if cid in cf_ids else ""
            print(f"    - {cid}: {slug} (cat={cat}){marker}{marker2}")
        print()

# Also check: do the EVALUATION steps (the ones producing unstable atoms) 
# use the lightweight protocol or the deterministic parser persona?
print(f"\n=== EVALUATION STEPS (Fast/Ensemble) AND THEIR PERSONA/PROTOCOL ===")
for s in steps:
    name = s.get("slug", s.get("id", "?"))
    strategy = s.get("model_strategy", "?")
    criteria_ids = s.get("criteria_block_ids", [])
    persona_id = s.get("execution_persona_block_id", None)
    
    has_lw = any(blocks.get(cid, {}).get("is_lightweight_protocol", False) for cid in criteria_ids)
    
    if strategy == "fast" and not has_lw:
        persona_slug = blocks.get(persona_id, {}).get("slug", "None") if persona_id else "None"
        # Check if this step has the deterministic parser persona 
        print(f"  {name}: strategy={strategy}, persona={persona_slug}, runs=3")
        # Check for zero-reasoning in criteria
        for cid in criteria_ids:
            b = blocks.get(cid, {})
            desc = b.get("ai_description", "")
            if "ZERO-REASONING" in desc or "zero-reasoning" in desc.lower():
                print(f"    *** HAS ZERO-REASONING in criteria: {b.get('slug')}")
