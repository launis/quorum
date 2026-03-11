import json
from pathlib import Path

def run_cleanup():
    seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
    with open(seed_path, encoding='utf-8') as f:
        data = json.load(f)

    # The ONLY workflow we want to keep
    target_workflow_id = "workflow_courtroom_20_full_audit"
    
    # 1. Filter workflows
    original_wf_count = len(data.get('workflows', []))
    data['workflows'] = [wf for wf in data.get('workflows', []) if wf['id'] == target_workflow_id]
    new_wf_count = len(data.get('workflows', []))
    
    # Get all steps used by this workflow
    target_workflow = data['workflows'][0]
    required_step_ids = set()
    for wf_step in target_workflow.get('steps', []):
        bp = wf_step.get('task_blueprint')
        if bp:
            required_step_ids.add(bp)
            
    # 2. Filter steps
    original_step_count = len(data.get('steps', []))
    data['steps'] = [step for step in data.get('steps', []) if step['id'] in required_step_ids]
    new_step_count = len(data.get('steps', []))

    # Get all prompt blocks used by these steps
    required_prompt_block_ids = set()
    for step in data['steps']:
        for pb in step.get('prompt_blocks', []):
            required_prompt_block_ids.add(pb)
            
    # Also add referenced prompt blocks in system_config or any default ones, just in case
    # Often, 'system_rule' category shouldn't be blindly deleted, but let's be surgical:
    # We will keep any prompt block that is actively referenced by surviving steps.
    
    # 3. Filter prompt blocks
    original_pb_count = len(data.get('prompt_blocks', []))
    
    # Wait, there might be global instructions used by the engine that aren't on steps directly.
    # Actually, in Quorum V2, all instructions are passed via the step's prompt_blocks array.
    # Exception: The System Config itself might have prompt overrides (not currently used in v2).
    # To be safe, let's keep all 'system_rule' category = 'domain_persona' or 'global' if they are used.
    # Since we are aggressive, let's keep only those explicitly linked to steps.
    
    # Also, some steps might use output_configs. Let's keep those intact as they are empty anyway.
    
    data['prompt_blocks'] = [pb for pb in data.get('prompt_blocks', []) if pb['id'] in required_prompt_block_ids]
    new_pb_count = len(data.get('prompt_blocks', []))

    # Save
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("=== SSOT V2 CLEANUP RESULTS ===")
    print(f"Workflows:     {original_wf_count} -> {new_wf_count}")
    print(f"Steps:         {original_step_count} -> {new_step_count}")
    print(f"Prompt Blocks: {original_pb_count} -> {new_pb_count}")
    print("All other workflows/steps/prompts have been purged.")

if __name__ == "__main__":
    run_cleanup()
