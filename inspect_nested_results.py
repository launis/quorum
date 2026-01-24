
import json
import sys

db_path = r"c:\src\quorum\data\db.json"
exec_key = "14"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    execution = data.get("executions", {}).get(exec_key)
    results = execution.get("results", {})
    step_results = results.get("step_results", {})
    
    print(f"Type of step_results: {type(step_results)}")
    if isinstance(step_results, dict):
        print(f"Keys in step_results: {list(step_results.keys())}")
        
        # Check Judge inside step_results
        judge = step_results.get("step_judge", {})
        print(f"\n--- JUDGE (Nested) ---")
        print(f"Status: {judge.get('status')}")
        output = judge.get("output", {})
        if isinstance(output, dict):
             print(f"Score Cards Keys: {output.get('score_cards', {}).keys() if isinstance(output.get('score_cards'), dict) else 'Not Dict'}")
             print(f"Total Score: {output.get('total_score')}")

except Exception as e:
    print(f"Error: {e}")
