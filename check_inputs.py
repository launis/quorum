import json

try:
    with open('data/db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for comp in data.get('components', {}).values():
        if comp.get('component_type') == 'step':
            inputs = comp.get('inputs', {})
            if isinstance(inputs, dict):
                for k, v in inputs.items():
                    if v is None:
                        print(f"Component Step {comp.get('id')} inputs[{k}] is null!")

    for w in data.get('workflows', {}).values():
        for step in w.get('steps', []):
            if isinstance(step, dict):
                inputs = step.get('inputs', {})
                if isinstance(inputs, dict):
                    for k, v in inputs.items():
                        if v is None:
                            print(f"Workflow {w['id']} step {step.get('id')} inputs[{k}] is null!")
                
                config = step.get('config', {})
                if isinstance(config, dict):
                    for k, v in config.items():
                        if v is None:
                            print(f"Workflow {w['id']} step {step.get('id')} config[{k}] is null!")

    print("Check finished.")
except Exception as e:
    print("Error:", e)
