import json
import os

SEED_PATH = os.path.join("backend", "seed", "seed_data.json")

def inspect_seed():
    if not os.path.exists(SEED_PATH):
        print(f"File not found: {SEED_PATH}")
        return

    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", {})
    found = False
    for wf_id, workflow in workflows.items():
        for step in workflow.get("steps", []):
            if step.get("id") == "step_falsifier":
                print(f"Workflow: {wf_id}")
                print(f"Task Key: {step.get('task_key')}")
                if "agent_class" in step.get("metadata", {}):
                     print(f"Metadata Agent Class: {step['metadata']['agent_class']}")
                found = True
    
    if not found:
        print("step_falsifier not found in seed_data.json.")

if __name__ == "__main__":
    inspect_seed()
