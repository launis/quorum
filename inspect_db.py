
import json
import sys

db_path = r"c:\src\quorum\data\db.json"
exec_id = "ee8703c2-e471-497c-b160-b8c4f8410d54"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    execution = data.get("executions", {}).get(exec_id)
    if not execution:
        print(f"Execution {exec_id} not found.")
        sys.exit(1)
        
    step_judge = execution.get("results", {}).get("step_judge", {})
    
    print("--- JUDGE STEP KEYS ---")
    print(step_judge.keys())
    
    output = step_judge.get("output", {})
    print("\n--- JUDGE OUTPUT KEYS ---")
    # If output is a string (some legacy versions), print it raw, otherwise keys
    if isinstance(output, str):
        print("Output is string length:", len(output))
        print("Preview:", output[:200])
    elif isinstance(output, dict):
        print(output.keys())
        print("\n--- SCORE CARDS ---")
        print(json.dumps(output.get("score_cards", "MISSING"), indent=2, ensure_ascii=False))
        print("\n--- DIMENSIONS ---")
        print(json.dumps(output.get("dimensions", "MISSING"), indent=2, ensure_ascii=False))
        print("\n--- TOTAL SCORE ---")
        print(output.get("total_score"))
    else:
        print("Output type:", type(output))

except Exception as e:
    print(f"Error: {e}")
