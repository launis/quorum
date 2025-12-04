import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"
TARGETS = ["principle_1", "method_2", "protocol_2"]

def audit_specific():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = {c['id']: c for c in data['components']}
    steps = data['steps']
    
    for tid in TARGETS:
        comp = components.get(tid)
        if not comp:
            print(f"{tid}: NOT FOUND in components.")
            continue
            
        print(f"\n{tid}: FOUND")
        print(f"  Name: {comp.get('name')}")
        print(f"  Content: {comp.get('content', '')[:100]}...")
        
        used_in = []
        for step in steps:
            if tid in step['execution_config']['llm_prompts']:
                used_in.append(step['id'])
        
        if used_in:
            print(f"  USED IN: {used_in}")
        else:
            print(f"  NOT USED in any step.")

if __name__ == "__main__":
    audit_specific()
