import sys
import os
import json
from tinydb import TinyDB, Query

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.engine import WorkflowEngine

def test_workflow_construction():
    print("Testing Workflow Construction...")
    
    # Initialize Engine with Mock DB
    engine = WorkflowEngine(db_path='data/db_mock.json')
    
    # Check if steps load
    steps = engine.db.table('steps').all()
    print(f"Loaded {len(steps)} steps from DB.")
    
    if len(steps) < 9:
        print("ERROR: Not all 9 steps loaded!")
        return
        
    # Preview Prompts for a few critical steps
    critical_steps = ['step_1', 'step_5', 'step_8']
    
    for s_id in critical_steps:
        print(f"\n--- Previewing Prompt for {s_id} ---")
        try:
            preview = engine.preview_step_prompt(s_id)
            system_instr = preview.get('system_instruction', '')
            
            # Check for Headers
            if "### MANDAATIT" in system_instr: print("  [OK] Mandates Header found")
            else: print("  [FAIL] Mandates Header MISSING")
            
            if "### SÄÄNNÖT" in system_instr: print("  [OK] Rules Header found")
            else: print("  [FAIL] Rules Header MISSING")
            
            if "### OHJEET" in system_instr: print("  [OK] Instructions Header found")
            else: print("  [FAIL] Instructions Header MISSING")
            
            # Check for Task
            if "KÄSKE: Toimi" in system_instr: print("  [OK] Task Command found")
            else: print("  [FAIL] Task Command MISSING")
            
            # Check for Specifics
            if s_id == 'step_5':
                if "Heuristiikka 1" in system_instr: print("  [OK] Heuristic 1 found")
                else: print("  [FAIL] Heuristic 1 MISSING")
                
        except Exception as e:
            print(f"ERROR previewing {s_id}: {e}")

if __name__ == "__main__":
    test_workflow_construction()
