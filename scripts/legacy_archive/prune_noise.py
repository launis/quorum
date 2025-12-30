import json
import os

SEED_FILE = "backend/database/seed_data.json"

def prune():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    steps = data.get('steps', [])
    
    # DEFINITION OF NOISE
    # Rules that only apply to Grading (Judge) or Reporting (XAI)
    GRADING_RULES = ["OP_RULE_4", "BARS_MATRIX"] 
    
    # Requirements that only apply to Analysis
    ANALYSIS_COMPONENTS = ["METHOD_1", "METHOD_2", "METHOD_3"]
    
    # LIST OF NON-GRADING STEPS
    # These steps should NOT have grading rules
    NON_GRADING_STEPS = [
        "step_guard", "step_analyst", "step_interaction", 
        "step_profiler", "step_detector", "step_overseer", "step_archivist"
    ]
    
    pruned_count = 0
    
    for step in steps:
        sid = step['id']
        prompts = step['execution_config']['llm_prompts']
        original_len = len(prompts)
        
        # 1. Prune Grading Rules from non-grading steps
        if sid in NON_GRADING_STEPS:
            prompts = [p for p in prompts if p not in GRADING_RULES]
            
        # 2. Prune Analysis Methods from simple checks (Guard/Overseer)
        if sid in ["step_guard", "step_overseer"]:
            prompts = [p for p in prompts if p not in ANALYSIS_COMPONENTS]
            
        if len(prompts) < original_len:
            print(f"Pruned {original_len - len(prompts)} items from {sid}")
            step['execution_config']['llm_prompts'] = prompts
            pruned_count += 1
            
    data['steps'] = steps
    
    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Pruning complete. Optimized {pruned_count} steps.")

if __name__ == "__main__":
    prune()
