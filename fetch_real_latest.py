
import json
import os
from datetime import datetime

DB_PATH = "data/db.json"

def fetch_latest_execution():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    executions = list(data.get("executions", {}).values())
    
    print(f"Total executions found: {len(executions)}")
    
    if not executions:
        return

    # Get last 5
    latests = executions[-5:]
    latests.reverse() # Newest first

    for i, execution in enumerate(latests):
        print(f"\n--- Execution {i} (Latest - {i}) ---")
        print(f"ID: {execution.get('id')}")
        print(f"Workflow ID: {execution.get('workflow_id')}")
        print(f"Status: {execution.get('status')}")
        print(f"Started: {execution.get('created_at', 'Unknown')}")
        
        inputs = execution.get("inputs", {})
        print(f"Inputs keys: {list(inputs.keys())}")
        
        history_text = inputs.get("history_text", "")
        
        if history_text is None:
             print("History Text: None")
        else:
             print(f"History Text Length: {len(history_text)}")
             clean_preview = str(history_text).replace("\n", "\\n")[:200]
             print(f"Preview: {clean_preview}...")

if __name__ == "__main__":
    fetch_latest_execution()
