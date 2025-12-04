import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def audit_steps():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = {c['id']: c for c in data['components']}
    steps = data['steps']
    
    print(f"Auditing {len(steps)} steps...\n")
    
    all_ok = True
    
    for step in steps:
        print(f"--- {step['id']}: {step['name']} ---")
        prompts = step['execution_config']['llm_prompts']
        missing = []
        
        for pid in prompts:
            if pid not in components:
                missing.append(pid)
        
        if missing:
            print(f"  [ERROR] Missing components: {missing}")
            all_ok = False
        else:
            print(f"  [OK] {len(prompts)} components linked.")
            # Optional: Print specific task component to verify it exists
            # task_comp = next((p for p in prompts if 'TASK' in p or 'task' in p), None)
            # if task_comp:
            #     print(f"  Task Component: {task_comp}")
            # else:
            #     print("  [WARNING] No explicit TASK component found in prompts (might be ok if instructions are elsewhere).")

    print("\nAudit complete.")
    if all_ok:
        print("RESULT: ALL STEPS OK (All referenced components exist).")
    else:
        print("RESULT: FAILURES DETECTED.")

if __name__ == "__main__":
    audit_steps()
