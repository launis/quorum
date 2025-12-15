import json
import os
import sys

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import get_db_path

def inspect_guard():
    # Force real DB if needed, or rely on finding db.json
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "db.json")
    print(f"Reading DB: {db_path}")
    
    if not os.path.exists(db_path):
        print("DB file not found.")
        return

    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    executions = data.get('executions', {})
    if not executions:
        print("No executions found.")
        return

    # Sort by key (or timestamp if available, but TinyDB keys are usually incremental ints as strings)
    # Assuming standard TinyDB structure { "1": {...}, "2": {...} }
    try:
        latest_id = sorted(executions.keys(), key=lambda x: int(x))[-1]
        latest = executions[latest_id]
        
        print(f"Latest Execution ID: {latest.get('execution_id')}")
        print(f"Status: {latest.get('status')}")
        print(f"Error: {latest.get('error')}")
        
        # Check step_guard in result or state
        # In DB, 'result' is usually the final output, but intermediate steps might be in 'outputs' if we store them?
        # Re-reading handler.py/engine.py: 
        # Engine updates `self.executions_table` with `result=...`.
        # On rejection, `result={"security_alert": ...}`.
        # But wait, does it save the full state?
        # Engine doesn't seem to save full state to `executions` table unless `completed`.
        # Use `result` field.
        
        print("Result:", json.dumps(latest.get('result'), indent=2))
        
        # IF the engine doesn't save the full `step_guard` object into `result` on failure, we might lose the detailed analysis!
        # Let's check if the previous steps output is saved.
        # Engine.py line 596: updates status='rejected', error='...', result={'security_alert': ...}
        # It DOES NOT appear to save the `step_guard` payload into the execution record on failure!
        # This is a debugging gap.
        
    except Exception as e:
        print(f"Error parsing executions: {e}")

if __name__ == "__main__":
    inspect_guard()
