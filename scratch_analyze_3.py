import json
import sys

def analyze_atoms(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    true_atoms = 0
    quotes_collected = 0
    
    for event in data:
        if event.get("event_type") == "output":
            content = event.get("content", {})
            
            # Count TRUE atoms
            for k, v in content.items():
                if isinstance(v, dict) and "evaluated_atoms" in v:
                    evaluated_atoms = v.get("evaluated_atoms", {})
                    for a_id, state in evaluated_atoms.items():
                        if state is True:
                            true_atoms += 1
                            
            # Count quotes collected
            if "atom_quotes" in content:
                for b_id, quotes in content["atom_quotes"].items():
                    quotes_collected += len(quotes)

    print(f"Total TRUE states: {true_atoms}")
    print(f"Total Quotes Collected: {quotes_collected}")

if __name__ == "__main__":
    analyze_atoms(sys.argv[1])
