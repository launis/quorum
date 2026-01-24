
import json
import sys

db_path = r"c:\src\quorum\data\db.json"
exec_key = "14" # Determined from previous list_executions output

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    execution = data.get("executions", {}).get(exec_key)
    if not execution:
        print(f"Execution Key {exec_key} not found.")
        sys.exit(1)
        
    print(f"Inspecting Execution ID: {execution.get('id')}")
    step_judge = execution.get("results", {}).get("step_judge", {})
    
    output = step_judge.get("output", {})
    
    if isinstance(output, str):
        print("Output is string length:", len(output))
        print("Preview:", output[:500])
    elif isinstance(output, dict):
        print("\n--- SCORE CARDS (RAW JSON) ---")
        print(json.dumps(output.get("score_cards", "MISSING"), indent=2, ensure_ascii=False))
        
        print("\n--- DIMENSIONS (RAW JSON) ---")
        print(json.dumps(output.get("dimensions", "MISSING"), indent=2, ensure_ascii=False))
        
        print("\n--- TOTAL SCORE ---")
        print(output.get("total_score"))
        
        print("\n--- FULL KEYS ---")
        print(output.keys())
    else:
        print("Output type:", type(output))

except Exception as e:
    print(f"Error: {e}")
