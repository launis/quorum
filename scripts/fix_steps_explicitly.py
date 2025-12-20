import json
import os

SEED_FILE = "backend/database/seed_data.json"

# Explicit mapping of Step ID -> Task Component
STEP_TO_TASK = {
    "step_guard": "TASK_GUARD",
    "step_analyst": "TASK_ANALYST",
    "step_profiler": "TASK_PROFILER",
    "step_logician": "TASK_LOGICIAN",
    "step_falsifier": "TASK_FALSIFIER",
    "step_causal": "TASK_CAUSAL",
    "step_detector": "TASK_PERFORMATIVITY", # detector -> performativity
    "step_overseer": "TASK_OVERSEER",
    "step_judge": "TASK_JUDGE",
    "step_xai": "TASK_XAI",
    "step_coach": "TASK_COACH",
    "step_archivist": "TASK_ARCHIVIST",
}

def fix_steps():
    try:
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Standard Sequence
        NEW_PROMPT_SEQUENCE_START = [
            "template_context_now",
            "HEADER_MANDATES",
            "MANDATE_1", "MANDATE_2", "MANDATE_3", "MANDATE_4",
            "HEADER_RULES",
            "RULE_1", "RULE_2", "RULE_3", "RULE_4", "RULE_5", "RULE_6",
            "OP_RULE_1", "OP_RULE_2", "OP_RULE_3", "OP_RULE_4",
            "HEADER_PROTOCOLS"
        ]
        
        steps = data.get('steps', [])
        for step in steps:
            sid = step.get('id')
            config = step.get('execution_config', {})
            prompts = config.get('llm_prompts', [])
            
            # 1. Determine Task
            task_id = STEP_TO_TASK.get(sid)
            if not task_id:
                # Fallback: Try to find existing TASK_ or instruction_
                for p in prompts:
                    if p.startswith("TASK_"): task_id = p; break
                    if p.startswith("instruction_"): task_id = p; break
            
            if not task_id:
                print(f"Skipping step {sid} (no mapped task)")
                continue
                
            # 2. Rebuild Prompts
            output_comps = [p for p in prompts if '_OUTPUT_' in p or 'template_output' in p]
            
            has_matrix = 'common_bars_matrix' in prompts or sid == 'step_judge'
            has_scientific = 'common_scientific_method' in prompts or sid in ['step_analyst', 'step_logician', 'step_falsifier', 'step_causal']
             
            new_prompts = list(NEW_PROMPT_SEQUENCE_START)
            if has_scientific: new_prompts.append("common_scientific_method")
            if has_matrix: new_prompts.append("common_bars_matrix")
            
            new_prompts.append("HEADER_INSTRUCTIONS")
            new_prompts.append(task_id) # Explicitly append the task
            
            new_prompts.extend(output_comps)
            
            # Preserve headers
            if "HEADER_TEXT" in prompts: new_prompts.append("HEADER_TEXT")
            if "DISCLAIMER_TEXT" in prompts: new_prompts.append("DISCLAIMER_TEXT")
            
            config['llm_prompts'] = new_prompts
            step['execution_config'] = config
            print(f"Fixed prompts for step {sid} -> {task_id}")
            
        data['steps'] = steps
        
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print("Steps fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing steps: {e}")

if __name__ == "__main__":
    fix_steps()
