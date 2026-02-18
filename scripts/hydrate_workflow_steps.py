
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SEED_FILE = PROJECT_ROOT / "backend" / "seed" / "seed_data.json"

def hydrate_steps():
    print(f"Reading seed file: {SEED_FILE}")
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading seed file: {e}")
        sys.exit(1)

    steps_definitions = {s["id"]: s for s in data.get("steps", [])}
    print(f"Loaded {len(steps_definitions)} step definitions.")
    
    workflows = data.get("workflows", [])
    print(f"Processing {len(workflows)} workflows...")
    
    modified_count = 0
    
    for wf in workflows:
        new_steps = []
        for step in wf.get("steps", []):
            step_id = step.get("id")
            if step_id in steps_definitions:
                definition = steps_definitions[step_id]
                # Merge definition into step, but let step override inputs/config if specific
                # Definition has: id, name, description, task_key, config
                # Workflow step has: id, inputs
                
                # We need task_key from definition at minimum.
                # Construct combined object
                hydrated = definition.copy()
                
                # Update with workflow-specific overlays (like inputs mapping)
                if "inputs" in step:
                    hydrated["inputs"] = step["inputs"]
                
                # Note: 'config' in definition is static config. 'inputs' are dynamic.
                # If workflow step has 'config' override, apply it? Usually workflow just has inputs.
                if "config" in step:
                     # deep merge? or replace? Replace for now.
                     hydrated["config"] = step["config"]
                     
                new_steps.append(hydrated)
                modified_count += 1
            else:
                print(f"Warning: Step ID '{step_id}' in workflow '{wf.get('id')}' not found in definitions. Leaving as-is.")
                new_steps.append(step)
        
        wf["steps"] = new_steps

    if modified_count > 0:
        print(f"Hydrated {modified_count} step references.")
        try:
            with open(SEED_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ Successfully saved {SEED_FILE}")
        except Exception as e:
            print(f"Error saving file: {e}")
            sys.exit(1)
    else:
        print("No steps needed hydration.")

if __name__ == "__main__":
    hydrate_steps()
