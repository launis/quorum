import json
from tinydb import TinyDB, Query, where

DB_PATH = 'data/db.json'

def fix_orphan_steps():
    db = TinyDB(DB_PATH)
    workflows_table = db.table('workflows')
    steps_table = db.table('steps')
    
    existing_steps = {s['id'] for s in steps_table.all()}
    print(f"Found {len(existing_steps)} existing steps in 'steps' table.")
    
    missing_steps = set()
    step_mapping = {} # step_id -> component_hint
    
    # 1. Scan Workflows
    for wf in workflows_table.all():
        steps = wf.get('steps', [])
        # 'steps' can be list of IDs or list of dicts?
        # Based on V2 Architecture, it SHOULD be list of IDs in 'steps' field,
        # OR list of dicts in 'steps' field (Embedded).
        # Repository likely handles normalizing.
        # But if Repository uses get_step_by_id(step_id), it hits 'steps' table.
        
        for s in steps:
            s_id = None
            if isinstance(s, dict):
                s_id = s.get('id')
            elif isinstance(s, str):
                s_id = s
                
            if s_id and s_id not in existing_steps:
                missing_steps.add(s_id)
                # Infer component
                if 'guard' in s_id: step_mapping[s_id] = 'guard'
                elif 'analyst' in s_id: step_mapping[s_id] = 'analyst'
                elif 'judge' in s_id: step_mapping[s_id] = 'judge'
                elif 'archivist' in s_id: step_mapping[s_id] = 'archivist'
                elif 'retrieve' in s_id: step_mapping[s_id] = 'retrieve_context'
                elif 'report' in s_id: step_mapping[s_id] = 'reporter'
                else: step_mapping[s_id] = 'generic_agent'

    print(f"Found {len(missing_steps)} missing steps: {missing_steps}")
    
    if not missing_steps:
        print("No missing steps found.")
        return

    # 2. Create Stubs
    new_steps = []
    for s_id in missing_steps:
        comp = step_mapping.get(s_id, 'guard')
        prompts = []
        if comp == 'guard': prompts = ['TASK_SECURITY_CHECK']
        elif comp == 'analyst': prompts = ['TASK_ANALYST']
        elif comp == 'judge': prompts = ['TASK_JUDGE', 'GLOBAL_CONTEXT']
        elif comp == 'reporter': prompts = ['TASK_REPORT']
        
        stub = {
            "id": s_id,
            "name": s_id.replace('_', ' ').capitalize(),
            "component": comp,
            "description": "Auto-generated stub to fix 404",
            "execution_config": {
                "llm_prompts": prompts,
                "model_strategy": "fast"
            },
            "output_config_component": None,
            "output_filename": f"{s_id}.json",
            "is_custom": False
        }
        new_steps.append(stub)
        
    # 3. Insert
    print(f"Inserting {len(new_steps)} stubs...")
    steps_table.insert_multiple(new_steps)
    print("Done.")

if __name__ == "__main__":
    fix_orphan_steps()
