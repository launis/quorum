
import json
import os

DB_PATH = "c:/src/quorum/data/db.json"

def inspect_exec_14():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        executions = data.get("executions", {})
        exec_14 = executions.get("14") # Keys are strings in JSON
        
        if not exec_14:
            print("Execution 14 not found.")
            return


        step_xai = exec_14.get("results", {}).get("step_xai")
        step_analyst = exec_14.get("results", {}).get("step_analyst")
        step_judge = exec_14.get("results", {}).get("step_judge")
        step_coach = exec_14.get("results", {}).get("step_coach")

        if step_analyst:
             print("Found 'step_analyst'.") 
        else:
             print("No 'step_analyst'.")

        if step_judge:
             print(f"Found 'step_judge'. Score: {step_judge.get('pisteet')} Verdict: {step_judge.get('tuomio')}")
             if "customer churn" in str(step_judge).lower():
                 print("WARNING: 'churn' found in Judge output!")
        else:
             print("No 'step_judge' found.")

        if step_coach:
             print(f"Found 'step_coach'. Plan items: {len(step_coach.get('toimenpiteet', []))}")
             if "churn" in str(step_coach).lower():
                 print("WARNING: 'churn' found in Coach output!")
        else:
             print("No 'step_coach' found.")

        if step_xai:
             print(f"XAI Verdict: {step_xai.get('final_verdict')}")
             if "churn" in str(step_xai).lower():
                 print("WARNING: 'churn' found in XAI Report!")
        else:
             print("No 'step_xai' found.")



    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_exec_14()
