
import json
from pathlib import Path

DB_PATH = Path("backend/database/db_mock.json")
TARGET_ID = "0fd84422-974c-43bb-8363-a2da1b8ef814"

def inspect_exec():
    if not DB_PATH.exists():
        print("DB not found")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    executions = data.get("executions", {})
    if not executions:
        # Maybe TinyDB format?
        default = data.get("_default", {})
        if default:
            executions = default
    
    target = None
    target_key = None
    
    # Try direct lookup first
    if TARGET_ID in executions:
        target = executions[TARGET_ID]
        target_key = TARGET_ID
    else:
        # Scan values
        for k, v in executions.items():
            if isinstance(v, dict) and v.get('execution_id') == TARGET_ID:
                target = v
                target_key = k
                break
    
    if not target:
        print(f"Execution {TARGET_ID} not found.")
        # print("Available keys:", list(executions.keys()))
        return

    print(f"--- Execution {TARGET_ID} (Key: {target_key}) ---")
    result = target.get('result', {})
    print("Result Keys:", list(result.keys()))
    
    step_judge = result.get('step_judge')
    if step_judge:
        print("✅ step_judge found")
        print("Keys in step_judge:", list(step_judge.keys()))
        pisteet = step_judge.get('pisteet')
        print("pisteet:", pisteet)
    else:
        print("❌ step_judge is Missing or None in 'result'")
        
        # Check if it exists in 'trace' (legacy location?)
        trace = target.get('trace', {})
        step_judge_trace = trace.get('step_judge')
        if step_judge_trace:
             print("✅ step_judge found in TRACE")
             print("pisteet in trace:", step_judge_trace.get('pisteet'))
        else:
             print("❌ step_judge missing in TRACE too.")

if __name__ == "__main__":
    inspect_exec()
