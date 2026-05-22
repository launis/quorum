import json

def inspect_full(path):
    print(f"\n=== Evaluative Matrices for {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    step_6 = data[6]
    content = step_6.get('content', {})
    eval_matrices = content.get('_evaluative_matrices', {})
    print("Full _evaluative_matrices:")
    for k, v in eval_matrices.items():
        print(f"  {k}: {v}")
    
    scoring_res = data[16].get('content', {}).get('scoring_result', {})
    print("Scoring Result:")
    for k, v in scoring_res.items():
        print(f"  {k}: {v}")

inspect_full("data/files/executions/exe_b6c7f868eccf4e8988889daf3ae1dfd4/execution_trace.json")
inspect_full("data/files/executions/exe_2609de8feb6e47db8222e7385c45a796/execution_trace.json")
