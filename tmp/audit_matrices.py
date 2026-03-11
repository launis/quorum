import json
from pathlib import Path

seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
with open(seed_path, encoding='utf-8') as f:
    d = json.load(f)

blocks = {b['id']: b['description']['translations'].get('fi', b['id']) for b in d.get('prompt_blocks', [])}

# Find all blocks that start with 'matrix_'
all_matrices = [b_id for b_id in blocks.keys() if b_id.startswith('matrix_')]

# For each matrix, find which steps use it
matrix_distribution = {m: [] for m in all_matrices}

for s in d.get('steps', []):
    prompts = s.get('prompt_blocks', [])
    for p in prompts:
        if p in matrix_distribution:
            matrix_distribution[p].append(s['id'])

print("=== MATRIX DISTRIBUTION AUDIT ===")
for m in sorted(matrix_distribution.keys()):
    steps_using = matrix_distribution[m]
    print(f"\nMatrix: {m} (Used in {len(steps_using)} steps)")
    for su in steps_using:
        print(f"  - {su}")

print("\n\n=== VERIFYING EACH CRITIC STEP (4-10) ===")
critic_steps = [
    'step_analyst', 'step_interaction_analyst', 'step_profiler', 
    'step_logician', 'step_falsifier', 'step_causal_analyst', 'step_performativity_detector'
]

for s_id in critic_steps:
    s = next((st for st in d.get('steps', []) if st['id'] == s_id), None)
    if s:
        print(f"\n{s_id}:")
        metrics = [p for p in s.get('prompt_blocks', []) if p.startswith('matrix_')]
        if not metrics:
            print("  (No matrices)")
        for m in metrics:
            print(f"  - {m}")
