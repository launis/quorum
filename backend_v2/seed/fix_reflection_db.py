from tinydb import TinyDB
import json

def fix_db():
    db = TinyDB('data/db_v2.json')
    table = db.table('task_blueprints')
    changes = 0
    target_blueprints = ['blueprint_analyst', 'blueprint_profiler', 'blueprint_logician', 'blueprint_falsifier', 'blueprint_causal', 'blueprint_overseer', 'blueprint_judge']
    
    # 1. Update TaskBlueprints in DB
    for bp in table.all():
        if bp.get('id') in target_blueprints or bp.get('slug') in target_blueprints:
            expected = bp.get('expected_inputs', {})
            if 'reflection_text' not in expected:
                expected['reflection_text'] = 'Optional reflection document or guided reflection.'
                # Update whole document
                table.update({'expected_inputs': expected}, doc_ids=[bp.doc_id])
                changes += 1
                
    print(f"Päivitettiin {changes} blueprinttiä TinyDB:ssä.")
    
    # Ensure also we update seed_data.json so NEXT seed run also brings them
    seed_path = "backend_v2/seed/seed_data.json"
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    seed_changes = 0
    for bp in data.get("task_blueprints", []):
        if bp.get('id') in target_blueprints or bp.get('slug') in target_blueprints:
             expected = bp.get('expected_inputs', {})
             if 'reflection_text' not in expected:
                 expected['reflection_text'] = 'Optional reflection document or guided reflection.'
                 bp['expected_inputs'] = expected
                 seed_changes += 1
                 
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Päivitettiin {seed_changes} blueprinttiä seed_data.json:ssa.")

if __name__ == "__main__":
    fix_db()
