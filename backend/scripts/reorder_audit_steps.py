import json
import os
import sys

SEED_FILE = os.path.join("backend", "seed", "seed_data.json")

def get_step_id(step_obj):
    return step_obj if isinstance(step_obj, str) else step_obj.get("id")

def reorder_workflows_safely():
    # 1. Load Data
    target_file = SEED_FILE
    if not os.path.exists(target_file):
        target_file = os.path.join("..", "seed", "seed_data.json")
    
    if not os.path.exists(target_file):
        print(f"CRITICAL: Seed file not found.")
        sys.exit(1)

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    workflows = data.get("workflows", [])
    updated_count = 0

    print(f"Analyzing {len(workflows)} workflows for 'step_context' repositioning...")

    for wf in workflows:
        wf_id = wf.get("id", "unknown")
        steps = wf.get("steps", [])
        step_ids = [get_step_id(s) for s in steps]
        
        # Skip if required steps aren't present
        if "step_guard" not in step_ids or "step_context" not in step_ids:
            continue

        # --- STATE SNAPSHOT (Integrity Lock) ---
        # We specifically track 'step_causal' to ensure it is untouched
        causal_exists = "step_causal" in step_ids
        
        original_len = len(steps)
        
        # Get current indices
        g_idx = step_ids.index("step_guard")
        c_idx = step_ids.index("step_context")

        # Logic: Context must be immediately after Guard
        if c_idx != g_idx + 1:
            print(f"[{wf_id}] Reordering: Context ({c_idx}) -> After Guard ({g_idx})...")
            
            # 1. Move Operation (Pop & Insert)
            context_node = steps.pop(c_idx)
            
            # Re-calculate guard index (indices shifted)
            new_ids_temp = [get_step_id(s) for s in steps]
            new_g_idx = new_ids_temp.index("step_guard")
            
            steps.insert(new_g_idx + 1, context_node)
            updated_count += 1
            
            # --- POST-OPERATION INTEGRITY CHECK ---
            final_ids = [get_step_id(s) for s in steps]
            
            # Check 1: List length
            if len(steps) != original_len:
                print(f"CRITICAL ERROR: Workflow length changed! {original_len} -> {len(steps)}")
                sys.exit(1)
            
            # Check 2: step_causal presence (Reference Integrity)
            if causal_exists:
                if "step_causal" not in final_ids:
                    print(f"CRITICAL ERROR: 'step_causal' LOST during move in {wf_id}!")
                    sys.exit(1)
                
            print(f"  -> Integrity OK. Causal reference preserved.")

    # 3. Commit Changes
    if updated_count > 0:
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"SUCCESS: Updated {updated_count} workflows. All integrity checks passed.")
        except Exception as e:
            print(f"Error saving JSON: {e}")
            sys.exit(1)
    else:
        print("No changes needed (Order is already correct).")

if __name__ == "__main__":
    reorder_workflows_safely()
