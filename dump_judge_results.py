
import json
import sys

db_path = r"c:\src\quorum\data\db.json"
exec_key = "14"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    execution = data.get("executions", {}).get(exec_key)
    results = execution.get("results", {}).get("step_results", {})
    judge = results.get("step_judge", {})
    output = judge.get("output", {})
    
    print("\n--- JUDGE OUTPUT (RAW) ---")
    print(json.dumps(output, indent=2, ensure_ascii=False)[:3000]) # Limit size

except Exception as e:
    print(f"Error: {e}")
