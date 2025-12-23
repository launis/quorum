
import json
import logging
import sys
from pathlib import Path

# Mock the environment to allow imports
sys.path.append(str(Path.cwd()))

try:
    from backend.models.state import WorkflowState
except ImportError as e:
    sys.exit(1)

DB_PATH = Path("backend/database/db_mock.json")
LOG_PATH = Path("migration_verify.log")

def check():
    with open(LOG_PATH, "w", encoding="utf-8") as log:
        def l(msg): log.write(msg + "\n")

        if not DB_PATH.exists():
            l(f"ERROR: DB not found at {DB_PATH}")
            return

        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        executions = data.get("executions", {})
        l(f"Found {len(executions)} executions.")
        
        for eid, exc in executions.items():
            if exc.get('status') != 'completed':
                continue
                
            l(f"\nChecking Execution {eid}...")
            res = exc.get('result', {})
            
            # Simulate ExecutionRouter logic
            hydration_data = res.copy()
            if 'execution_id' not in hydration_data:
                hydration_data['execution_id'] = exc.get('execution_id', 'unknown')
            if 'inputs' not in hydration_data:
                hydration_data['inputs'] = exc.get('inputs', {})
                
            try:
                state = WorkflowState(**hydration_data)
                flat = state.to_flat_dict()
                keys = list(flat.keys())
                l(f"  Hydration: SUCCESS")
                l(f"  Keys: {keys}")
                
                if "System_Status" in keys:
                    l("  ✅ System_Status PRESENT")
                    st = flat["System_Status"]
                    l(f"     Content Keys: {list(st.keys())}")
                else:
                    l("  ❌ System_Status MISSING")
                    
                if "Scores" in keys:
                    l("  ✅ Scores PRESENT")
                    # Check if scores are empty
                    if not flat["Scores"]:
                        l("     ⚠️ Scores is EMPTY dict")
                    else:
                        l(f"     Content Keys: {list(flat['Scores'].keys())}")
                else:
                    l("  ❌ Scores MISSING")
                    
            except Exception as e:
                l(f"  ❌ Hydration FAILED: {e}")

if __name__ == "__main__":
    check()
