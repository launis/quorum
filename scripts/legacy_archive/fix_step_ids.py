import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

ID_MAP = {
    "step_5_causal": "step_5_overseer",
    "step_6_performativity": "step_6_causal",
    "step_7_overseer": "step_7_performativity"
}

def fix_ids():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    steps = data['steps']
    workflows = data['workflows']
    
    # Update Step IDs
    for step in steps:
        if step['id'] in ID_MAP:
            old = step['id']
            new = ID_MAP[old]
            step['id'] = new
            print(f"Renamed step ID: {old} -> {new}")
            
    # Update Workflows
    for wf in workflows:
        new_steps = []
        for s in wf['steps']:
            if s in ID_MAP:
                new_steps.append(ID_MAP[s])
            else:
                new_steps.append(s)
        wf['steps'] = new_steps
        print(f"Updated workflow {wf['id']}")

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Step IDs fixed.")

if __name__ == "__main__":
    fix_ids()
