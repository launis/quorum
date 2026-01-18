
import json

def find_steps():
    path = 'c:/src/quorum/backend/seed/seed_data.json'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    workflow_start = -1
    in_workflows = False
    
    for i, line in enumerate(lines):
        if '"workflows": [' in line:
            in_workflows = True
            print(f"Workflows array starts at line {i+1}")
            continue
            
        if in_workflows:
            # Simple heuristic to find workflow IDs and their steps
            if '"id":' in line:
                print(f"Workflow ID at line {i+1}: {line.strip()}")
            if '"steps": [' in line:
                print(f"  Steps start at line {i+1}: {line.strip()}")
                # Print next few lines to see content
                for offset in range(1, 5):
                    if i+offset < len(lines):
                        print(f"    Line {i+1+offset}: {lines[i+offset].strip()}")

if __name__ == "__main__":
    find_steps()
