import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"
TARGETS = ["principle_1", "method_2", "protocol_2"]

def remove_unused():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data['components']
    steps = data['steps']
    
    to_remove = []
    
    for tid in TARGETS:
        # Check if exists
        comp = next((c for c in components if c['id'] == tid), None)
        if not comp:
            print(f"{tid}: Not found.")
            continue
            
        # Check usage
        used = False
        for step in steps:
            if tid in step['execution_config']['llm_prompts']:
                used = True
                print(f"{tid}: USED in {step['id']}")
                break
        
        if not used:
            print(f"{tid}: NOT USED. Removing...")
            to_remove.append(tid)
        else:
            print(f"{tid}: Content: {comp.get('content')}")

    if to_remove:
        data['components'] = [c for c in components if c['id'] not in to_remove]
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Removed {len(to_remove)} components.")
    else:
        print("Nothing to remove.")

if __name__ == "__main__":
    remove_unused()
