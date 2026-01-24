
import json

db_path = r"c:\src\quorum\data\db.json"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get("executions", {})
    for eid, details in executions.items():
        # Check explicit total_score
        res = details.get("results", {})
        # Check root hoisting (legacy)
        if str(res.get("total_score")) == "83.33" or str(res.get("total_score")) == "83.3":
             print(f"Found match in Root Results: Key {eid} (ID: {details.get('id')})")
        
        # Check step_judge
        step_judge = res.get("step_results", {}).get("step_judge", {}).get("output", {})
        if str(step_judge.get("total_score")) == "83.33" or str(step_judge.get("total_score")) == "83.3":
             print(f"Found match in Step Judge: Key {eid} (ID: {details.get('id')})")
             print(f"Keys in output: {step_judge.keys()}")

except Exception as e:
    print(f"Error: {e}")
