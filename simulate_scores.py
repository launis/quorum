import json
import os
import hashlib
from collections import defaultdict

CACHE_PATH = r"c:\src\quorum\backend_v2\seed\atomization_cache.json"
EXE1 = r"c:\src\quorum\data\files\executions\exe_6a3184b794264f6bbbb16c21102b7954"
EXE2 = r"c:\src\quorum\data\files\executions\exe_c83d4eb23cef4a4e9aeaa4ea38a1d820"

def load_atom_mapping():
    mapping = {}
    blocks_meta = {}
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for pb_id, scales in data.items():
        blocks_meta[pb_id] = {"scales": []}
        for scale in scales:
            s_val = float(scale.get("score"))
            blocks_meta[pb_id]["scales"].append(s_val)
            for claim in scale.get("claims", []):
                for text in claim.get("micro_atoms", []):
                    atom_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
                    mapping[atom_hash] = {
                        "block_id": pb_id,
                        "score": s_val,
                        "text": text
                    }
        blocks_meta[pb_id]["scale_min"] = min(blocks_meta[pb_id]["scales"])
        blocks_meta[pb_id]["scale_max"] = max(blocks_meta[pb_id]["scales"])
        
    return mapping, blocks_meta

def find_evaluations(obj, results):
    if isinstance(obj, dict):
        if "evaluations" in obj and isinstance(obj["evaluations"], list):
            if len(obj["evaluations"]) > 0 and isinstance(obj["evaluations"][0], dict) and "atom_id" in obj["evaluations"][0]:
                results.append(obj["evaluations"])
        for v in obj.values():
            find_evaluations(v, results)
    elif isinstance(obj, list):
        for item in obj:
            find_evaluations(item, results)

def calculate_waterfall_floor(stats, scale_min, threshold=0.75):
    sorted_levels = sorted(stats.keys())
    floor_score = scale_min

    for level in sorted_levels:
        level_data = stats[level]
        total = level_data["total"]
        hits = level_data["hits"]
        pct = (hits / total) if total > 0 else 0.0

        if pct >= threshold:
            floor_score = level
        else:
            break
            
    return floor_score

def calculate_dampening(stats, scale_min, scale_max):
    achieved_score = scale_min
    modifier = 1.0
    prev_level = scale_min
    sorted_levels = sorted(stats.keys())
    
    for level in sorted_levels:
        total = stats[level]["total"]
        hits = stats[level]["hits"]
        hit_rate = (hits / total) if total > 0 else 0
        
        if level == scale_min:
            modifier = hit_rate
        else:
            step_value = (level - prev_level)
            achieved_score += step_value * hit_rate * modifier
            modifier = modifier * hit_rate
        prev_level = level
        
    return min(scale_max, max(scale_min, achieved_score))

def process_execution(exe_path, atom_mapping, blocks_meta):
    results = []
    
    trace_path = os.path.join(exe_path, "execution_trace.json")
    if os.path.exists(trace_path):
        with open(trace_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            find_evaluations(data, results)
            
    context_path = os.path.join(exe_path, "frozen_context.json")
    if not results and os.path.exists(context_path):
        with open(context_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            find_evaluations(data, results)

    if not results:
        return f"No evaluations found in {os.path.basename(exe_path)}"

    block_scale_stats = defaultdict(lambda: defaultdict(lambda: {"hits": 0, "total": 0}))
    
    best_evs = max(results, key=len)
    
    for ev in best_evs:
        atom_id = ev.get("atom_id")
        boolean_val = ev.get("boolean", False)
        
        mapping = atom_mapping.get(atom_id)
        if not mapping:
            hashed_id = hashlib.md5(atom_id.encode("utf-8")).hexdigest() if atom_id else ""
            mapping = atom_mapping.get(hashed_id)
            
        if mapping:
            pb_id = mapping["block_id"]
            s_val = mapping["score"]
            block_scale_stats[pb_id][s_val]["total"] += 1
            if boolean_val:
                block_scale_stats[pb_id][s_val]["hits"] += 1

    out = [f"=== Execution: {os.path.basename(exe_path)} ==="]
    for pb_id, stats in block_scale_stats.items():
        meta = blocks_meta[pb_id]
        scale_min = float(meta["scale_min"])
        scale_max = float(meta["scale_max"])
        
        floor_score = calculate_waterfall_floor(stats, scale_min, 0.75)
        dampening_score = calculate_dampening(stats, scale_min, scale_max)
        
        # Calculate raw percentage (hits/total_atoms) mapped over total scale
        total_hits = sum(d["hits"] for d in stats.values())
        total_atoms = sum(d["total"] for d in stats.values())
        raw_weighted = scale_min + ((scale_max - scale_min) * (total_hits / total_atoms)) if total_atoms > 0 else scale_min
        
        old_hybrid = min(raw_weighted, floor_score + 1.0)
        
        out.append(f"\nMatrix (PromptBlock): {pb_id}")
        out.append(f"Scale Min: {scale_min}, Max: {scale_max}")
        for lvl in sorted(stats.keys()):
            h = stats[lvl]['hits']
            t = stats[lvl]['total']
            pct = int((h/t)*100) if t>0 else 0
            out.append(f"  - Level {lvl}: {h}/{t} ({pct}%)")
            
        out.append(f"\n[Tulos 1] Nykyinen malli (Hybrid Cap): {old_hybrid:.2f}")
        out.append(f"          (Weighted: {raw_weighted:.2f}, Floor: {floor_score:.1f} -> Katto: {floor_score+1.0})")
        out.append(f"[Tulos 2] Uusi malli (Progressive Dampening): {dampening_score:.2f}")
    
    return "\n".join(out)

if __name__ == "__main__":
    b_map, b_meta = load_atom_mapping()
    print(process_execution(EXE1, b_map, b_meta))
    print("\n" + "="*50 + "\n")
    print(process_execution(EXE2, b_map, b_meta))
