import json

def check_hooks():
    with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("--- HOOK MAPPINGS: workflow_courtroom_20_full_audit ---")
    
    workflows = data.get('workflows', {})
    wf = None
    for w in workflows.values():
        if w['id'] == 'workflow_courtroom_20_full_audit':
            wf = w
            break
            
    if not wf:
        print("Workflow not found!")
        return
        
    for step in wf.get('steps', []):
        task_id = step.get('task_blueprint')
        
        # Check if overridden in workflow step
        step_hooks = step.get('hooks', [])
        
        # Check blueprint
        blueprint = None
        for b in data.get('steps', {}).values():
            if b['id'] == task_id:
                blueprint = b
                break
                
        blueprint_hooks = blueprint.get('hooks', []) if blueprint else []
        
        if step_hooks:
            print(f"[{task_id}] -> Workflow Overridden Hooks: {step_hooks}")
        elif blueprint_hooks:
            print(f"[{task_id}] -> Inherited Blueprint Hooks: {blueprint_hooks}")
        else:
            print(f"[{task_id}] -> NO HOOKS ATTACHED")

if __name__ == '__main__':
    check_hooks()
