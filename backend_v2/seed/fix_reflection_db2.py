from tinydb import TinyDB
import json

def fix_all():
    db = TinyDB('data/db_v2.json')
    seed_path = "backend_v2/seed/seed_data.json"
    
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Poistetaan turhat expected_inputs TaskBlueprinteista, jotta rakenne vastaa Pydanticia
    #    Sekä kannasta että JSON-siemenestä.
    bp_table = db.table('task_blueprints')
    for bp in bp_table.all():
        if 'expected_inputs' in bp:
            del bp['expected_inputs']
            bp_table.update(bp, doc_ids=[bp.doc_id])

    for bp in data.get('task_blueprints', []):
         if 'expected_inputs' in bp:
            del bp['expected_inputs']

    # 2. Lisätään input_mappings oikeasti Workflown _nodien_ määrittelyihin. (Workflows.steps)
    # HUOM: YAML-vastaava seed_data.json ja TinyDB on vähän eri muodossa työnkulkujen (workflows) osalta
    target_blueprints = ['task_analyst', 'task_profiler', 'task_logician', 'task_falsifier', 'task_causal', 'task_overseer', 'task_judge']
    
    wf_table = db.table('workflows')
    wf_changes = 0
    # Kanta-ajo
    for wf in wf_table.all():
        steps = wf.get('steps', [])
        for step in steps:
             if step.get('task_blueprint') in target_blueprints:
                 mappings = step.get('input_mappings', {})
                 if 'reflection_text' not in mappings:
                     mappings['reflection_text'] = '$inputs.reflection_text'
                     wf_changes += 1
        wf_table.update({'steps': steps}, doc_ids=[wf.doc_id])
        
    print(f"Päivitettiin {wf_changes} nodea kannan workflows.steps alta.")
    
    # JSON-ajo
    seed_changes = 0
    for wf in data.get('workflows', []):
         steps = wf.get('steps', [])
         for step in steps:
             if step.get('task_blueprint') in target_blueprints:
                 mappings = step.get('input_mappings', {})
                 if 'reflection_text' not in mappings:
                     mappings['reflection_text'] = '$inputs.reflection_text'
                     seed_changes += 1
                     
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"Päivitettiin {seed_changes} nodea seed_data.json:n workflows.steps alta.")
    
    
if __name__ == "__main__":
    fix_all()
