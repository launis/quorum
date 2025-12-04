import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

RENAME_MAP = {
    "criteria_1": "criteria_analysis_efficiency",
    "criteria_2": "criteria_evaluation_argumentation",
    "criteria_3": "criteria_synthesis_creativity"
}

def rename_criteria():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Rename Components
    for comp in data['components']:
        if comp['id'] in RENAME_MAP:
            old_id = comp['id']
            new_id = RENAME_MAP[old_id]
            comp['id'] = new_id
            # Update name field too if it's generic
            if "criteria_" in comp['name'].lower(): 
                 # Extract title from content first line
                 title = comp['content'].split('\n')[0]
                 # Remove "KRITEERI X: " prefix
                 if ":" in title:
                     comp['name'] = title.split(':', 1)[1].strip()
                 else:
                     comp['name'] = title
            print(f"Renamed component {old_id} -> {new_id}")

    # 2. Update Step 8 Prompts
    step8 = next((s for s in data['steps'] if s['id'] == 'step_8'), None)
    if step8:
        prompts = step8['execution_config']['llm_prompts']
        new_prompts = []
        for p in prompts:
            if p in RENAME_MAP:
                new_prompts.append(RENAME_MAP[p])
            else:
                new_prompts.append(p)
        step8['execution_config']['llm_prompts'] = new_prompts
        print("Updated Step 8 prompts with new criteria IDs.")

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Rename complete.")

if __name__ == "__main__":
    rename_criteria()
