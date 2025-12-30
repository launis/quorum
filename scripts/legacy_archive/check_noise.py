from tinydb import TinyDB, Query
import os

def check():
    db = TinyDB('backend/database/db_mock.json')
    query = Query()
    steps = db.table('steps')
    
    guard = steps.search(query.id == 'step_guard')
    if not guard:
        print("Guard not found")
        return
        
    prompts = guard[0]['execution_config']['llm_prompts']
    
    has_op_rule_4 = "OP_RULE_4" in prompts
    has_method_1 = "METHOD_1" in prompts
    
    print(f"Guard prompts count: {len(prompts)}")
    print(f"Has OP_RULE_4 (Grading Sanction): {has_op_rule_4}")
    print(f"Has METHOD_1 (Red Team): {has_method_1}")
    
    if has_op_rule_4:
        print("DETECTED NOISE: Guard does not need grading sanctions.")

if __name__ == "__main__":
    check()
