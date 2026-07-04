"""Comprehensive analysis: For each step blueprint used in the workflow,
count how many atoms the atom_flattening_hook would produce (before sampling),
and what schema_max_evaluations must be to fit them."""
import json

with open("data/db_v2.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Build block map from DB
block_map = {}
for table_name, table_data in db.items():
    if isinstance(table_data, dict):
        for k, v in table_data.items():
            if isinstance(v, dict) and v.get("id", "").startswith("blk_"):
                block_map[v["id"]] = v

# Build blueprint map
bp_map = {}
for table_name, table_data in db.items():
    if isinstance(table_data, dict):
        for k, v in table_data.items():
            if isinstance(v, dict) and v.get("id", "").startswith("sp_"):
                bp_map[v["id"]] = v

# Workflow steps
with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    sd = json.load(f)

wf = sd["workflows"][0]
print(f"Workflow: {wf['id']}")
print("=" * 80)

for step in wf["steps"]:
    step_id = step["id"]
    bp_id = step["task_blueprint"]
    bp = bp_map.get(bp_id)
    if not bp:
        print(f"\n  Step {step_id} -> Blueprint {bp_id}: NOT FOUND IN DB")
        continue
    
    pre_hooks = bp.get("pre_hooks", [])
    has_atom_flattening = "atom_flattening_hook" in pre_hooks
    criteria_ids = bp.get("criteria_block_ids", [])
    
    # Count matrix blocks and their TDAs
    matrix_blocks = []
    criteria_blocks = []
    for cid in criteria_ids:
        blk = block_map.get(cid)
        if not blk:
            continue
        cat = blk.get("category_id", "?")
        if cat == "matrix":
            scales = blk.get("scales", [])
            total_tda = 0
            for sc in scales:
                for cl in sc.get("claims", []):
                    total_tda += len(cl.get("tda_assertions", []))
            matrix_blocks.append((cid, len(scales), total_tda))
        else:
            criteria_blocks.append(cid)
    
    print(f"\n  Step {step_id} -> Blueprint {bp_id}")
    print(f"    Pre-hooks: {pre_hooks}")
    print(f"    Has atom_flattening: {has_atom_flattening}")
    print(f"    Criteria blocks: {len(criteria_blocks)}")
    print(f"    Matrix blocks: {len(matrix_blocks)}")
    
    if has_atom_flattening:
        total_atoms = 0
        for mid, n_scales, n_tda in matrix_blocks:
            print(f"      Matrix {mid}: {n_scales} scales, {n_tda} total TDAs")
            total_atoms += n_tda
        print(f"    *** TOTAL ATOMS (shuffled): {total_atoms}")
        print(f"    *** With schema_max_evaluations=18, fits in 1 schema: {total_atoms <= 18}")
        print(f"    *** With schema_max_evaluations=7, fits in 1 schema: {total_atoms <= 7}")
    else:
        print(f"    Non-matrix step, criteria count = {len(criteria_blocks)}")
