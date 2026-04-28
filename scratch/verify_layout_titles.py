import json

def verify_changes():
    bak_path = 'c:/src/quorum/backend_v2/seed/seed_data.json.title_bak'
    new_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
    
    with open(bak_path, 'r', encoding='utf-8') as f:
        bak_data = json.load(f)
        
    with open(new_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
        
    def compare_dicts(d1, d2, path=""):
        if type(d1) != type(d2):
            return [f"Type mismatch at {path}"]
            
        if isinstance(d1, dict):
            keys1 = set(d1.keys())
            keys2 = set(d2.keys())
            diffs = []
            for k in keys1.union(keys2):
                new_path_str = f"{path}.{k}" if path else k
                if "output_profiles" in new_path_str and "layouts" in new_path_str and (new_path_str.endswith(".title") or new_path_str.endswith(".description")):
                    continue
                if k not in d1:
                    diffs.append(f"Key added: {new_path_str}")
                elif k not in d2:
                    diffs.append(f"Key removed: {new_path_str}")
                else:
                    diffs.extend(compare_dicts(d1[k], d2[k], new_path_str))
            return diffs
        elif isinstance(d1, list):
            if len(d1) != len(d2):
                return [f"List length mismatch at {path}: {len(d1)} != {len(d2)}"]
            diffs = []
            for i, (item1, item2) in enumerate(zip(d1, d2)):
                diffs.extend(compare_dicts(item1, item2, f"{path}[{i}]"))
            return diffs
        else:
            if d1 != d2:
                return [f"Value mismatch at {path}: {d1} != {d2}"]
            return []

    diffs = compare_dicts(bak_data, new_data)
    if diffs:
        print("[FAIL] Illegal changes detected outside of layout title and description!")
        for d in diffs:
            print("  ", d)
    else:
        print("[PASS] Only allowed changes detected (layout title and description).")

    blocks = {b['id']: b for b in new_data.get('prompt_blocks', [])}
    matrix_ids = {b['id'] for b in blocks.values() if b.get('category_id') == 'matrix'}
    
    if len(matrix_ids) != 13:
        print(f"[FAIL] Expected 13 matrix blocks in database, found {len(matrix_ids)}.")
        return
        
    targeted_counts = {m: 0 for m in matrix_ids}
    
    for prof in new_data.get('output_profiles', []):
        for layout in prof.get('layouts', []):
            if layout.get('preset_view') in ['1d_metrics', '2d_compare', '3d_matrix', '3d_complex']:
                targets = layout.get('target_blocks', [])
                for t in targets:
                    if t in targeted_counts:
                        targeted_counts[t] += 1
                        
    coverage_fail = False
    for m, count in targeted_counts.items():
        if count != 1:
            print(f"[FAIL] Matrix {m} ({blocks[m].get('slug')}) is targeted {count} times (Expected: exactly 1).")
            coverage_fail = True
            
    if not coverage_fail:
        print("[PASS] All 13 matrices are present exactly once in the layout target_blocks.")

if __name__ == '__main__':
    verify_changes()
