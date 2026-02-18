import json
import os
import shutil

SEED_PATH = os.path.join("backend", "seed", "seed_data.json")

def fix_seed_falsifier():
    if not os.path.exists(SEED_PATH):
        print(f"File not found: {SEED_PATH}")
        return

    # Backup
    shutil.copy(SEED_PATH, SEED_PATH + ".bak_global_seed")
    print(f"Backed up {SEED_PATH} to {SEED_PATH}.bak_global_seed")

    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return

    if "steps" in data and isinstance(data["steps"], list):
        found = False
        for step in data["steps"]:
            if step.get("id") == "step_falsifier":
                print("Found 'step_falsifier' in global steps of seed_data.json.")
                
                # Ensure metadata exists
                if "metadata" not in step:
                    step["metadata"] = {}
                
                # Check and fix agent_class
                current_class = step["metadata"].get("agent_class")
                if current_class != "LogicalFalsifierAgent":
                    print(f"  -> Updating agent_class from '{current_class}' to 'LogicalFalsifierAgent'")
                    step["metadata"]["agent_class"] = "LogicalFalsifierAgent"
                    found = True
                else:
                    print("  -> agent_class is already correct.")
        
        if found:
            with open(SEED_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Successfully updated global step_falsifier in seed_data.json.")
        else:
            print("No changes needed or step not found in global 'steps' list.")
    else:
        print("No global 'steps' list found in seed_data.json.")

if __name__ == "__main__":
    fix_seed_falsifier()
