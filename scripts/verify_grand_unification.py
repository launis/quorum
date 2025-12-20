from tinydb import TinyDB, Query
import os
import sys

def verify_full_suite():
    db_path = 'backend/database/db_mock.json'
    if not os.path.exists(db_path):
        db_path = 'backend/database/db_prod.json'
        
    print(f"Verifying DB at: {db_path}")
    db = TinyDB(db_path)
    
    # 1. Check New Component Presence
    comps = db.table('components')
    Component = Query()
    
    required_ids = [
        "GLOBAL_CONTEXT", "HEADER_MANDATES", "MANDATE_1", "OP_RULE_4",
        "PROTOCOL_1", "METHOD_1", "HEURISTIC_1", "PRINCIPLE_1",
        "TASK_INTERACTION", "TASK_ARCHIVIST", "TASK_COACH",
        "BARS_MATRIX"
    ]
    
    for rid in required_ids:
        if not comps.search(Component.id == rid):
            print(f"FAIL: Missing Component {rid}")
            sys.exit(1)
            
    print("PASS: All critical components found.")
    
    # 2. Check Workflow Steps Wiring
    steps = db.table('steps')
    
    # Check step_guard for GLOBAL_CONTEXT (Index 0)
    guard = steps.search(Query().id == 'step_guard')[0]
    prompts = guard['execution_config']['llm_prompts']
    
    if prompts[0] != "GLOBAL_CONTEXT":
        print(f"FAIL: step_guard does not start with GLOBAL_CONTEXT. Got: {prompts[0]}")
        sys.exit(1)
        
    if "TASK_GUARD" not in prompts:
         print("FAIL: step_guard missing TASK_GUARD")
         sys.exit(1)
         
    print("PASS: step_guard wiring correct (Global Context + Task).")
    
    # Check step_judge for Strict Matrix
    judge = steps.search(Query().id == 'step_judge')[0]
    j_prompts = judge['execution_config']['llm_prompts']
    
    if "BARS_MATRIX" not in j_prompts:
        print("FAIL: step_judge missing BARS_MATRIX")
        sys.exit(1)
        
    print("PASS: step_judge wiring correct.")
    
    # Check Workflow Chain
    wf = db.table('workflows').search(Query().id == 'sequential_audit_chain')[0]
    wf_steps = wf['steps']
    
    if len(wf_steps) != 13:
        print(f"FAIL: Workflow step count mismatch. Expected 13, got {len(wf_steps)}")
        sys.exit(1)
        
    if "step_interaction" not in wf_steps:
        print("FAIL: Workflow missing step_interaction")
        sys.exit(1)
        
    print("PASS: Workflow chain correct (13 steps).")
    print("GRAND UNIFICATION VERIFIED.")

if __name__ == "__main__":
    verify_full_suite()
