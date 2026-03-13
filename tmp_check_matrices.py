import json

db = json.load(open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8', errors='ignore'))
pb = db.get('prompt_blocks', [])

user_output = {
    "block_taskguard": 0,
    "matrix_archivist": 5.0,
    "block_taskarchivist": 5,
    "matrix_kahneman": 9.0,
    "matrix_goodhart": 3.0,
    "matrix_falsifier": 4,
    "matrix_causal_analyst": 5.0,
    "matrix_causal_abductive": 4.0,
    "block_taskcausal": 1,
    "matrix_toulmin": 4.0,
    "matrix_bloom": 5.0,
    "matrix_judge": 5.0,
    "matrix_xai_reporter": 5,
    "block_taskxai": 5,
    "block_taskcoach": 5
}

expected_matrices = {m.get('id'): m for m in pb if m.get('type') in ('float', 'string', 'int')}

print("=== MATRIX VERIFICATION ===")
matrices_checked = 0
for k, v in user_output.items():
    if k in expected_matrices:
        m = expected_matrices[k]
        s_min = m.get('scale_min')
        s_max = m.get('scale_max')
        is_valid = s_min <= float(v) <= s_max if s_min is not None and s_max is not None else "N/A"
        print(f"[{'OK' if is_valid is True else 'ERROR' if is_valid is False else '?'}] {k}: {v} (Expected: {s_min}-{s_max})")
        matrices_checked += 1
    else:
        print(f"[UNKNOWN] {k}: {v} (Not found in prompt_blocks)")

print(f"\nTotal expected matrices defined in DB: {len(expected_matrices)}")
for k, m in expected_matrices.items():
    if k not in user_output:
        print(f"MISSING IN OUTPUT: {k}")
