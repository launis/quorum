
import json
import os

DB_PATH = r"c:\src\quorum\data\db.json"

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load DB: {e}")
        return

    workflows = data.get("workflows", {})
    
    # 1. Build Template Map from a known good workflow (Workflow 2 or 3)
    # We look for ANY workflow that has object-based steps to use as a source of truth for definitions.
    step_templates = {}
    
    # Scan all workflows for object steps to build a library of definitions
    for wf_id, wf in workflows.items():
        steps = wf.get("steps", [])
        if not steps:
            continue
            
        # If first item is dict, this is a modern workflow
        if isinstance(steps[0], dict):
            for step in steps:
                step_id = step.get("id")
                if step_id and step_id not in step_templates:
                    step_templates[step_id] = step
    
    print(f"Found {len(step_templates)} step templates.")

    # 2. Iterate and Migrate
    migrated_count = 0
    for wf_id, wf in workflows.items():
        steps = wf.get("steps", [])
        if not steps:
            continue

        # Check if legacy (list of strings)
        if isinstance(steps[0], str):
            print(f"Migrating Workflow {wf_id} ({wf.get('name')}) from Strings to Objects...")
            new_steps = []
            for step_id in steps:
                if step_id in step_templates:
                    # Copy definition
                    new_steps.append(step_templates[step_id].copy())
                else:
                    # Create generic fallback if NO template found (should not happen for standard steps)
                    print(f"  WARNING: No template found for '{step_id}', generating generic fallback.")
                    task_key = step_id.replace("step_", "")
                    new_steps.append({
                        "id": step_id,
                        "task_key": task_key,
                        "inputs": {
                            "history_text": "$history_text",
                            "product_text": "$product_text", 
                            "reflection_text": "$reflection_text"
                        },
                        "config": {"model_strategy": "fast"}
                    })
            
            wf["steps"] = new_steps
            migrated_count += 1
        
        # Also clean up "default_model_mapping" as it's deprecated by Step Config
        if "default_model_mapping" in wf:
             # We can optionaly remove it, but user didn't explicitly ask. 
             # Let's leave it for now to avoid side effects, staying focused on Steps.
             pass

    if migrated_count > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully migrated {migrated_count} workflows.")
    else:
        print("No legacy workflows found to migrate.")

if __name__ == "__main__":
    migrate_db()
