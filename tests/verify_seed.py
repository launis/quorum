
import json
import os

SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"

def check_seed():
    if not os.path.exists(SEED_PATH):
        print(f"Seed file not found: {SEED_PATH}")
        return

    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        workflows = data.get("workflows", {})
        print(f"Found {len(workflows)} workflows.")
        
        for wf_id, wf in workflows.items():
            print(f"\nWorkflow: {wf_id}")
            steps = wf.get("steps", [])
            print(f"  Step Count: {len(steps)}")
            found_falsifier = False
            for step in steps:
                step_id = step.get("id")
                print(f"  - Step: {step_id} (Task: {step.get('task_key')})")
                if step_id == "step_falsifier":
                    found_falsifier = True
            
            if not found_falsifier:
                print(f"  --> ALERT: step_falsifier is MISSING in {wf_id}!")

    except Exception as e:
        print(f"Error reading seed: {e}")

if __name__ == "__main__":
    check_seed()
