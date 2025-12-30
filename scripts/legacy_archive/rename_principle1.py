import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def rename_principle():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Rename Component
    comp = next((c for c in data['components'] if c['id'] == 'principle_1'), None)
    if comp:
        comp['id'] = 'principle_falsification'
        comp['name'] = 'Falsifiointiperiaate'
        print("Renamed principle_1 -> principle_falsification")
    
    # Update Steps
    for step in data['steps']:
        prompts = step['execution_config']['llm_prompts']
        if 'principle_1' in prompts:
            step['execution_config']['llm_prompts'] = [
                'principle_falsification' if p == 'principle_1' else p for p in prompts
            ]
            print(f"Updated prompts in {step['id']}")

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Done.")

if __name__ == "__main__":
    rename_principle()
