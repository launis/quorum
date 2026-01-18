
import json

def resolve_inputs(input_mapping, state):
    resolved = {}
    for k, v in input_mapping.items():
        if isinstance(v, str) and v.startswith("$"):
            path = v[1:]
            parts = path.split(".")
            current = state
            try:
                for part in parts:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        current = getattr(current, part)
                    if current is None:
                         break
                resolved[k] = current
            except (KeyError, AttributeError) as e:
                print(f"Failed to resolve {path}: {e}")
                resolved[k] = None
        else:
            resolved[k] = v
    return resolved

def main():
    try:
        with open("data/db.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading db.json: {e}")
        return
    
    wfs_table = data.get("workflows", {})
    if not wfs_table:
         # Maybe default table?
         wfs_table = data.get("_default", {})

    print(f"Found {len(wfs_table)} workflows in DB.")
    
    found_panel_step = False
    
    for doc_id, wf in wfs_table.items():
        steps = wf.get("steps", [])
        for step in steps:
            if step.get("task_key") == "panel":
                found_panel_step = True
                inputs = step.get("inputs", {})
                print(f"\nVerifying Panel Step in Workflow '{wf.get('id')}'...")
                print(f"Input Mapping: {inputs}")
                
                # 1. Structural Check
                vals = str(inputs.values())
                if "$inputs." in vals:
                    print("FAIL: '$inputs.' prefix detected!")
                else:
                    print("PASS: No '$inputs.' prefix found.")
                
                # 2. Simulation
                mock_state = {
                    "history_text": "ACTUAL_HISTORY",
                    "product_text": "ACTUAL_PRODUCT",
                    "reflection_text": "ACTUAL_REFLECTION",
                    "step_analyst": {"some": "data"}
                }
                
                print("Simulating resolution with state keys:", list(mock_state.keys()))
                resolved = resolve_inputs(inputs, mock_state)
                print(f"Resolved Inputs: {resolved}")
                
                if resolved.get("history_text") == "ACTUAL_HISTORY":
                    print("SUCCESS: history_text resolved correctly.")
                else:
                    print("FAILURE: history_text did NOT resolve.")

    if not found_panel_step:
        print("\nWARNING: No 'panel' task found in any workflow.")

if __name__ == "__main__":
    main()
