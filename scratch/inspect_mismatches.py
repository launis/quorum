import json
import os
import glob

def get_all_evals(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_evals = {}
    for step in data:
        if 'content' in step and isinstance(step['content'], dict):
            for e in step['content'].get('evaluations', []):
                all_evals[e['atom_id']] = e
    return all_evals

exe_dirs = glob.glob('data/files/executions/exe_*')
exe_dirs.sort(key=os.path.getmtime, reverse=True)

if len(exe_dirs) < 2:
    print("Not enough executions.")
    exit(1)

run_1_path = os.path.join(exe_dirs[1], 'execution_trace.json')
run_2_path = os.path.join(exe_dirs[0], 'execution_trace.json')

print(f"Comparing Run 1 ({exe_dirs[1]}) and Run 2 ({exe_dirs[0]})")

evals_1 = get_all_evals(run_1_path)
evals_2 = get_all_evals(run_2_path)

# Let's inspect a few mismatching atoms in detail
mismatches = ["tda_d46093a71bbbcd79", "tda_247927c98b0c46f8", "tda_0871942d6add46f1", "tda_8f668ea29869ba8b", "tda_6be555cac0b9115b"]

for atom_id in mismatches:
    if atom_id in evals_1 and atom_id in evals_2:
        print("\n" + "="*80)
        print(f"ATOM: {atom_id}")
        print("RUN 1:")
        print(json.dumps(evals_1[atom_id], indent=2, ensure_ascii=False))
        print("RUN 2:")
        print(json.dumps(evals_2[atom_id], indent=2, ensure_ascii=False))
