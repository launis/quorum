
import json
import sys

db_path = r"c:\src\quorum\data\db.json"
# The partial ID from log/screenshot
target_id_partial = "7f12c342"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get("executions", {})
    found = False
    
    for eid, details in executions.items():
        if target_id_partial in details.get("id", ""):
            found = True
            print(f"--- Execution ID: {details.get('id')} ---")
            print(f"Status: {details.get('status')}")
            print(f"Current Step: {details.get('current_step')}")
            
            results = details.get("results", {})
            step_results = results.get("step_results", {})
            
            print("\n--- Completed Steps ---")
            for step_id, res in step_results.items():
                print(f"- {step_id}")
            
            # Check Overseer specifically
            overseer = step_results.get("step_overseer")
            if overseer:
                print(f"\n[OK] Overseer is DONE.")
            else:
                print(f"\n[PENDING] Overseer is NOT in results.")
                
            # Check Archivist
            archivist = step_results.get("step_archivist")
            if archivist:
                print(f"[OK] Archivist is DONE.")
            else:
                print(f"[PENDING] Archivist is NOT in results.")

    if not found:
        print("Execution not found.")

except Exception as e:
    print(f"Error: {e}")
