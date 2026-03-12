import json
import copy

def update_workflow_blocks():
    target_file = r'c:\src\quorum\backend_v2\seed\seed_data.json'
    with open(target_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    wf = next(w for w in data['workflows'] if w['id'] == 'workflow_courtroom_20_full_audit')
    coach_step = next(s for s in wf['steps'] if s['task_blueprint'] == 'step_coach')
    
    # In V2, the step data usually inherits prompt_blocks from the TaskBlueprint in `steps` table 
    # OR overrides it in the workflow. Let's see if it's currently defined as an empty list.
    print(f"Current blocks in workflow step: {coach_step.get('prompt_blocks')}")
    
    blueprint = next(s for s in data['steps'] if s['id'] == 'step_coach')
    print(f"Current blocks in blueprint: {len(blueprint.get('prompt_blocks', []))}")
    
    # If the workflow overrides with [], delete the empty list so it inherits from blueprint
    if 'prompt_blocks' in coach_step and coach_step['prompt_blocks'] == []:
        del coach_step['prompt_blocks']
        print("Deleted empty prompt_blocks from workflow step to force blueprint inheritance.")
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    update_workflow_blocks()
