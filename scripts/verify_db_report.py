
import json
import os
from datetime import datetime

DB_PATH = "c:/src/quorum/data/db.json"

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        executions = data.get("executions", {})
        if not executions:
            print("No executions found in DB.")
            return


        # Look for specific ID or latest
        target_id = "b6939dfb-3cbe-48df-bf71-8dc3e20be7cc"
        if target_id in executions:
             print(f"Found Target Execution ID: {target_id}")
             latest_exec = executions[target_id]
             latest_id = target_id
        else:
            print(f"Target ID {target_id} not found. checking latest...")
             # Sort by started_at to find the latest
            sorted_executions = sorted(
                executions.items(),
                key=lambda x: x[1].get("started_at", ""),
                reverse=True
            )
            latest_id, latest_exec = sorted_executions[0]
            
        print(f"Checking Execution ID: {latest_id}")

        print(f"Latest Execution ID: {latest_id}")
        print(f"Started At: {latest_exec.get('started_at')}")
        print(f"Status: {latest_exec.get('status')}")

        # Check Top Level
        if "xai_report_formatted" in latest_exec:
            print("SUCCESS: 'xai_report_formatted' found at TOP LEVEL.")
            print(f"Report Length: {len(latest_exec['xai_report_formatted'])} chars")
            print("Preview: " + latest_exec['xai_report_formatted'][:100] + "...")
        else:
            print("FAILURE: 'xai_report_formatted' NOT found at TOP LEVEL.")


        # Check Step Level
        step_xai = latest_exec.get("results", {}).get("step_xai")
        if step_xai:
            print("Found 'step_xai' in results.")
            if isinstance(step_xai, dict):
                # Check for formatted report
                if "xai_report_formatted" in step_xai:
                     print("INFO: 'xai_report_formatted' found inside 'step_xai'.")
                else:
                     print("INFO: 'xai_report_formatted' NOT found inside 'step_xai' dict.")
                
                # Check for structured fields
                verdict = step_xai.get("final_verdict")
                confidence = step_xai.get("confidence_score")
                print(f"STRUCTURAL CHECK: Verdict='{verdict}', Confidence='{confidence}'")
            else:
                 print(f"INFO: 'step_xai' is type {type(step_xai)}")
        else:
             print("INFO: 'step_xai' NOT found in results.")


    except Exception as e:
        print(f"Error reading DB: {e}")

if __name__ == "__main__":
    check_db()
