import json
import os
import shutil

FILES_TO_FIX = [
    os.path.join("data", "db.json"),
    os.path.join("backend", "seed", "seed_data.json")
]

def fix_falsifier_in_steps(steps_container):
    changes = False
    
    # Handle list
    if isinstance(steps_container, list):
        for step in steps_container:
            if step.get("id") == "step_falsifier":
                if _fix_step(step):
                    changes = True
    
    # Handle dict (where values are steps)
    elif isinstance(steps_container, dict):
        for key, step in steps_container.items():
            if isinstance(step, dict) and step.get("id") == "step_falsifier":
                print(f"  -> Found in dict with key '{key}'")
                if _fix_step(step):
                    changes = True
                    
    return changes

def _fix_step(step):
    fixed = False
    if "metadata" not in step:
        step["metadata"] = {}
    
    current_class = step["metadata"].get("agent_class")
    if current_class != "LogicalFalsifierAgent":
        print(f"    -> Updating agent_class from '{current_class}' to 'LogicalFalsifierAgent'")
        step["metadata"]["agent_class"] = "LogicalFalsifierAgent"
        fixed = True
    else:
        print("    -> agent_class is already correct.")
    return fixed

def process_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\nProcessing {file_path}...")
    
    # Backup
    backup_path = file_path + ".bak_meta_fix"
    shutil.copy(file_path, backup_path)
    print(f"Backed up to {backup_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    changes_made = False
    
    # Check global steps
    if "steps" in data:
        print("Found global 'steps'.")
        if fix_falsifier_in_steps(data["steps"]):
            changes_made = True
            print("Fixed global step_falsifier.")
    else:
        print("No global 'steps' found.")

    # Check embedded workflows (just in case)
    if "workflows" in data:
        wfs = data["workflows"]
        if isinstance(wfs, dict):
            wfs = wfs.values() # Iterate dict values
        
        if isinstance(wfs, (list, tuple)):
            for wf in wfs:
                if "steps" in wf:
                    if fix_falsifier_in_steps(wf["steps"]):
                        changes_made = True
                        print(f"Fixed step_falsifier in workflow {wf.get('id')}")

    if changes_made:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved updates to {file_path}")
    else:
        print("No changes required.")

if __name__ == "__main__":
    for f in FILES_TO_FIX:
        process_file(f)
