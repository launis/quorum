import json
import os

db_path = "data/db.json"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

with open(db_path, encoding="utf-8") as f:
    try:
        data = json.load(f)
        executions = data.get("executions", {})
        print(f"Found {len(executions)} executions in DB.")
        for key, value in executions.items():
            eid = value.get('id')
            status = value.get('status')
            results = value.get('results', {})
            print(f"ID: {eid}, Status: {status}")
            print(f"Results Keys: {list(results.keys())}")
            if 'step_results' in results:
                print(f"Step Results: {list(results['step_results'].keys())}")

    except Exception as e:
        print(f"Error reading DB: {e}")
