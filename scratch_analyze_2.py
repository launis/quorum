import json
import sys
from collections import Counter

def analyze_atoms(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    atom_states = Counter()
    total_matrices = 0
    
    print("=== Execution Analysis ===")
    
    for event in data:
        if event.get("event_type") == "output":
            content = event.get("content", {})
            
            # The scoring output stores the matrices as their block IDs.
            for k, v in content.items():
                if isinstance(v, dict) and "evaluated_atoms" in v:
                    total_matrices += 1
                    evaluated_atoms = v.get("evaluated_atoms", {})
                    for a_id, state in evaluated_atoms.items():
                        if state == "DLQ":
                            atom_states["DLQ"] += 1
                        elif state is True:
                            atom_states["TRUE"] += 1
                        elif state is False:
                            atom_states["FALSE"] += 1
                        else:
                            atom_states[str(state)] += 1

    print(f"Total Matrices: {total_matrices}")
    print(f"Atom States: {dict(atom_states)}")

if __name__ == "__main__":
    analyze_atoms(sys.argv[1])
