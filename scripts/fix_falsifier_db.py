import json
import os
import shutil

DB_PATH = os.path.join("data", "db.json")

def fix_falsifier_step():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    # Backup
    shutil.copy(DB_PATH, DB_PATH + ".bak")
    print(f"Backed up {DB_PATH} to {DB_PATH}.bak")

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", {})
    fixed_count = 0

    for wf_id, workflow in workflows.items():
        steps = workflow.get("steps", [])
        for step in steps:
            if step.get("id") == "step_falsifier":
                current_key = step.get("task_key")
                print(f"Found step_falsifier in workflow {wf_id}. Current task_key: {current_key}")
                
                if current_key != "falsifier":
                    print(f"  -> FIXING: Changing task_key from '{current_key}' to 'falsifier'")
                    step["task_key"] = "falsifier"
                    fixed_count += 1
                else:
                    print("  -> Step is already correct.")

    if fixed_count > 0:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully fixed {fixed_count} instances of step_falsifier.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    fix_falsifier_step()
