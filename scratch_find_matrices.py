import json
import os

folder = r'C:\src\quorum\data\files\executions\exe_a2f8229bcb264fbe885c48b9aca22f3e'
state_path = os.path.join(folder, 'frozen_context.json')

if os.path.exists(state_path):
    with open(state_path, encoding='utf-8') as f:
        state = json.load(f)

    print(f"Final Score: {state.get('final_score')}")
    print(f"Penalties: {state.get('penalties')}")

    # Try to find matrices
    def find_matrices(obj):
        if isinstance(obj, dict):
            if '_evaluative_matrices' in obj:
                print('Found _evaluative_matrices:', obj['_evaluative_matrices'])
            for k, v in obj.items():
                find_matrices(v)
        elif isinstance(obj, list):
            for i in obj:
                find_matrices(i)

    find_matrices(state)
