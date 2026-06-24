import json
import sys

def print_atom(run_id, atom_id):
    path = f"data/files/executions/{run_id}/execution_trace.json"
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    for step in data:
        if 'content' in step and isinstance(step['content'], dict):
            evals = step['content'].get('evaluations')
            if isinstance(evals, list):
                for e in evals:
                    if e.get('atom_id') == atom_id:
                        print(f"--- RUN {run_id} ---")
                        print(json.dumps(e, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    print_atom("exe_119e27721f40489dae493a04ec25e985", "tda_b120e2c0a40840358df1e64a4b788b30")
    print_atom("exe_bfbeb34b577b42bfae90c251bb5d42be", "tda_b120e2c0a40840358df1e64a4b788b30")
