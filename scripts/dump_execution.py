import json

with open("c:/src/quorum/data/db_v2.json", "r", encoding="utf-8") as f:
    db = json.load(f)

executions = db.get("executions", {})
if executions:
    # Get the last execution visually
    last_exec = list(executions.values())[-1]
    
    print(f"Execution ID: {last_exec.get('id')}")
    print(f"Final Score: {last_exec.get('final_score')}")
    
    print("\nMatrices:")
    data = last_exec.get("data", {})
    for key, value in data.items():
        if isinstance(key, str) and key.endswith("_normalized"):
            print(f"{key}: {value}")
        if isinstance(key, str) and key.endswith("_is_evaluative"):
            print(f"{key}: {value}")
else:
    print("No executions found.")
