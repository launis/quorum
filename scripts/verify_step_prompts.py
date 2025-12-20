from tinydb import TinyDB
import os
import sys

def verify_step():
    db_path = 'backend/database/db_mock.json'
    if not os.path.exists(db_path):
        db_path = 'backend/database/db_prod.json'
        
    print(f"Checking DB: {db_path}")
    db = TinyDB(db_path)
    steps = db.table('steps').all()
    
    if not steps:
        print("FAIL: No steps found.")
        sys.exit(1)
        
    step1 = steps[0]
    prompts = step1['execution_config']['llm_prompts']
    
    print(f"Step 1 ({step1['id']}) Prompts: {prompts}")
    
    required = ['HEADER_MANDATES', 'MANDATE_1', 'HEADER_RULES', 'OP_RULE_1', 'HEADER_INSTRUCTIONS', 'TASK_GUARD']
    missing = [r for r in required if r not in prompts]
    
    if missing:
        print(f"FAIL: Missing required prompts: {missing}")
        sys.exit(1)
        
    print("PASS: All required prompts found in Step 1.")

if __name__ == "__main__":
    verify_step()
