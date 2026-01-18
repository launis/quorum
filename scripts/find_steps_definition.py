
import json

def find_step_def():
    path = 'c:/src/quorum/backend/seed/seed_data.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    steps = data.get('steps', [])
    for step in steps:
        if step.get('id') == 'step_analyst':
            print(json.dumps(step, indent=2))
            return

if __name__ == "__main__":
    find_step_def()
