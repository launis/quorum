
import json
import os
from datetime import datetime

DB_PATH = "data/db.json"
OUTPUT_PATH = "latest_execution.json"

def get_latest_execution():
    if not os.path.exists(DB_PATH):
        print(f"Error: DB file not found at {DB_PATH}")
        return

    try:
        with open(DB_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading DB: {e}")
        return

    executions = data.get("executions", {})
    if not executions:
        print("No executions found in DB.")
        return

    # Convert dictionary to list
    execution_list = []
    if isinstance(executions, dict):
        execution_list = list(executions.values())
    elif isinstance(executions, list):
        execution_list = executions
    else:
        print(f"Unknown executions format: {type(executions)}")
        return

    if not execution_list:
        print("No executions list found.")
        return

    # Sort by started_at
    def parse_time(exec_item):
        ts = exec_item.get("started_at")
        if not ts:
            return datetime.min
        try:
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except ValueError:
            return datetime.min

    execution_list.sort(key=parse_time, reverse=True)
    latest = execution_list[0]

    print(f"Found {len(execution_list)} executions.")
    print(f"Latest Execution ID: {latest.get('id')}")
    print(f"Workflow ID: {latest.get('workflow_id')}")
    print(f"Started At: {latest.get('started_at')}")
    print(f"Status: {latest.get('status')}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        json.dump(latest, out, indent=2, ensure_ascii=False)

    print(f"Saved latest execution to: {OUTPUT_PATH}")

if __name__ == "__main__":
    get_latest_execution()
