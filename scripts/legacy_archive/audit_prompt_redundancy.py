import json
from collections import Counter

SEED_FILE = "backend/database/seed_data.json"

def audit_prompts():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    components = {c['id']: c for c in data.get('components', [])}
    
    # 1. Check for duplicates and legacy mix
    for step in data.get('steps', []):
        sid = step['id']
        prompts = step.get('execution_config', {}).get('llm_prompts', [])
        
        # Check Duplicates
        counts = Counter(prompts)
        dupes = [p for p, c in counts.items() if c > 1]
        
        # Check Legacy Mixing (TASK_ vs instruction_)
        tasks = [p for p in prompts if p.startswith("TASK_")]
        instructions = [p for p in prompts if p.startswith("instruction_") and not p.startswith("INSTRUCTION_")] # Exclude new HEADER/INSTRUCTION categories if named INSTRUCTION_
        
        # Check Description Priority
        missing_desc = []
        for pid in prompts:
            comp = components.get(pid)
            if comp and not comp.get('description'):
                missing_desc.append(pid)
                
        if dupes or (tasks and instructions) or missing_desc:
            print(f"--- Step: {sid} ---")
            if dupes: print(f"  DUPLICATES: {dupes}")
            if tasks and instructions: print(f"  MIXED LEGACY: {tasks} AND {instructions}")
            if missing_desc: print(f"  MISSING DESC: {missing_desc}")

if __name__ == "__main__":
    audit_prompts()
