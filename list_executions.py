
import json

db_path = r"c:\src\quorum\data\db.json"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get("executions", {})
    print(f"Found {len(executions)} executions.")
    for eid, details in executions.items():
        print(f"ID: {eid} | Status: {details.get('status')} | Workflow: {details.get('workflow_id')}")

except Exception as e:
    print(f"Error: {e}")
