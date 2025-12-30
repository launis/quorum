import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

STEP_MAP = {
    "step_1": "step_1_guard",
    "step_2": "step_2_analyst",
    "step_3": "step_3_logician",
    "step_4": "step_4_falsifier",
    "step_5": "step_5_causal",
    "step_6": "step_6_performativity",
    "step_7": "step_7_overseer",
    "step_8": "step_8_judge",
    "step_9": "step_9_xai"
}

def rename_steps():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Rename Steps
    for step in data['steps']:
        if step['id'] in STEP_MAP:
            old_id = step['id']
            new_id = STEP_MAP[old_id]
            step['id'] = new_id
            print(f"Renamed step {old_id} -> {new_id}")

    # 2. Update Workflows
    for wf in data['workflows']:
        new_steps = []
        for s_id in wf['steps']:
            if s_id in STEP_MAP:
                new_steps.append(STEP_MAP[s_id])
            else:
                new_steps.append(s_id)
        wf['steps'] = new_steps
        print(f"Updated workflow {wf['id']} steps.")

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Step rename complete.")

if __name__ == "__main__":
    rename_steps()
