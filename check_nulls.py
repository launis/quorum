import json

def check_null_strings(data):
    workflows = data.get('workflows', {})
    if isinstance(workflows, dict):
        workflows = workflows.values()
        
    print(f"Checking {len(workflows)} workflows...")
    for w in workflows:
        if w.get('id') is None: print(f"Workflow {w.get('name')} id is null")
        if w.get('name') is None: print(f"Workflow {w.get('id')} name is null")
        if w.get('description') is None: print(f"Workflow {w.get('id')} description is null")
        if w.get('organization_id') is None: print(f"Workflow {w.get('id')} organization_id is null")
        
        for step in w.get('steps', []):
            if isinstance(step, dict):
                if step.get('id') is None: print(f"Workflow {w.get('id')} -> Step has null id")
                if step.get('task_key') is None: print(f"Workflow {w.get('id')} -> Step {step.get('id')} task_key is null")
                if step.get('name') is None: print(f"Workflow {w.get('id')} -> Step {step.get('id')} name is null")
            
        scoring_logic = w.get('scoring_logic', [])
        for rule in scoring_logic:
            if rule.get('label') is None: print(f"Workflow {w.get('id')} -> rule label is null")

try:
    with open('data/db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    check_null_strings(data)
except Exception as e:
    print("Error:", e)
