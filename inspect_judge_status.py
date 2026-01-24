
import json
import sys

db_path = r"c:\src\quorum\data\db.json"
exec_key = "14"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    execution = data.get("executions", {}).get(exec_key)
    if not execution:
        print(f"Execution Key {exec_key} not found.")
        sys.exit(1)
        
    step_judge = execution.get("results", {}).get("step_judge", {})
    
    print(f"Status: {step_judge.get('status')}")
    print(f"Error: {step_judge.get('error')}")
    
    # Check Inputs (did it get the previous steps?)
    inputs = step_judge.get("inputs", {})
    print("\n--- INPUT KEYS ---")
    print(inputs.keys())
    
    # Check Analyst Input size
    analyst_data = inputs.get("todistus_kartta", {})
    if isinstance(analyst_data, dict):
         print(f"Analyst Data Keys: {analyst_data.keys()}")
    else:
         print(f"Analyst Data Type: {type(analyst_data)}")

except Exception as e:
    print(f"Error: {e}")
