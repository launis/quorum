from tinydb import TinyDB, Query
import os
import sys

def verify():
    # Detect DB
    db_path = 'backend/database/db_mock.json'
    if not os.path.exists(db_path):
        db_path = 'backend/database/db_prod.json'
    
    print(f"Verifying DB at: {db_path}")
    db = TinyDB(db_path)
    table = db.table('components')
    
    # 1. Check for Mandate Headers
    Component = Query()
    res_header = table.search(Component.id == 'HEADER_MANDATES')
    if not res_header:
        print("FAIL: HEADER_MANDATES not found.")
        sys.exit(1)
    print("PASS: HEADER_MANDATES found.")
    
    # 2. Check Judge Instruction Content (Competence Pivot)
    # Note: We renamed instruction_judge to TASK_JUDGE
    res_judge = table.search(Component.id == 'TASK_JUDGE')
    if not res_judge:
        print("FAIL: TASK_JUDGE not found.")
        sys.exit(1)
        
    content = res_judge[0].get('content', '')
    if "PROMPT-KOMPETENSSA" not in content and "PROMPT-KOMPETENSSIA" not in content:
        # Note: Typo tolerance or exact string match. The script had "PROMPT-KOMPETENSSIA"
        print(f"FAIL: TASK_JUDGE content does not match expectations. Got: {content[:100]}...")
        sys.exit(1)
    print("PASS: TASK_JUDGE content updated.")

    # 3. Check Analyst Instruction (Context Audit)
    res_analyst = table.search(Component.id == 'TASK_ANALYST')
    if not res_analyst:
        print("FAIL: TASK_ANALYST not found.")
        sys.exit(1)
    
    content = res_analyst[0].get('content', '')
    if "Context Audit" not in content:
        print(f"FAIL: instruction_analyst content does not match 'Context Audit'. Got: {content[:100]}...")
        sys.exit(1)
    print("PASS: instruction_analyst content updated.")
    
    print("ALL CHECKS PASSED.")

if __name__ == "__main__":
    verify()
