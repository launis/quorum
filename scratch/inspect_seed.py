import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    sd = json.load(f)

print("Top-level keys:", list(sd.keys()))
wfs = sd.get("workflows", [])
print(f"Workflows: {len(wfs)}")
for wf in wfs:
    steps = wf.get("steps", [])
    wf_id = wf.get("id", "?")
    print(f"  WF {wf_id}: {len(steps)} steps")
    for s in steps:
        print(f"    Step {s['id']} -> blueprint {s['task_blueprint']}")

bps = sd.get("step_blueprints", [])
print(f"Step blueprints in seed: {len(bps)}")

# Now check which blueprints are in db_v2
with open("data/db_v2.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Find all step blueprints in the DB
bp_count = 0
for table_name, table_data in db.items():
    if isinstance(table_data, dict):
        for k, v in table_data.items():
            if isinstance(v, dict) and v.get("id", "").startswith("sp_"):
                bp_count += 1
                bid = v["id"]
                crit_ids = v.get("criteria_block_ids", [])
                print(f"  DB Blueprint {bid}: {len(crit_ids)} criteria blocks")
                # Count matrix blocks
                for cid in crit_ids:
                    for t2, t2d in db.items():
                        if isinstance(t2d, dict) and cid in t2d:
                            blk = t2d[cid]
                            cat = blk.get("category_id", "?")
                            if cat == "matrix":
                                scales = blk.get("scales", [])
                                total_tda = 0
                                for sc in scales:
                                    for cl in sc.get("claims", []):
                                        total_tda += len(cl.get("tda_assertions", []))
                                print(f"    -> MATRIX {cid}: {len(scales)} scales, {total_tda} total TDAs")

print(f"Total blueprints in DB: {bp_count}")
