import json
import os

DB_PATH = os.path.join("data", "db.json")

def inspect_falsifier():
    if not os.path.exists(DB_PATH):
        print(f"File not found: {DB_PATH}")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", {})
    found = False
    for wf_id, workflow in workflows.items():
        for step in workflow.get("steps", []):
            if step.get("id") == "step_falsifier":
                print(f"Workflow: {wf_id}")
                print(json.dumps(step, indent=2))
                found = True
    
    if not found:
        print("step_falsifier not found in any workflow.")

if __name__ == "__main__":
    inspect_falsifier()
