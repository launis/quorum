import json

def check_hooks():
    with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("--- PRE AND POST HOOK MAPPINGS: workflow_courtroom_20_full_audit ---")
    
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
        step_pre = step.get('pre_hooks', [])
        step_post = step.get('post_hooks', [])
        
        # Check blueprint
        blueprint = None
        for b in data.get('steps', {}).values():
            if b['id'] == task_id:
                blueprint = b
                break
                
        blueprint_pre = blueprint.get('pre_hooks', []) if blueprint else []
        blueprint_post = blueprint.get('post_hooks', []) if blueprint else []
        
        pre = step_pre if step_pre else blueprint_pre
        post = step_post if step_post else blueprint_post
        
        if pre or post:
            print(f"[{task_id}]")
            if pre:
                print(f"  PRE:  {pre}")
            if post:
                print(f"  POST: {post}")
        else:
            print(f"[{task_id}] -> NO HOOKS ATTACHED")

if __name__ == '__main__':
    check_hooks()
