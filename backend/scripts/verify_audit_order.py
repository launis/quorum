import json
import os
import sys

SEED_FILE = os.path.join("backend", "seed", "seed_data.json")

def get_step_id(step_obj):
    return step_obj if isinstance(step_obj, str) else step_obj.get("id")

def verify_final_state():
    target_file = SEED_FILE
    if not os.path.exists(target_file):
        target_file = os.path.join("..", "seed", "seed_data.json")

    with open(target_file, encoding='utf-8') as f:
        data = json.load(f)

    workflows = data.get("workflows", [])
    errors = 0

    print("Verifying Workflow Order and Content...")

    # 1. Build Registry Index
    registry_step_ids = {s.get("id") for s in data.get("steps", [])}

    for wf in workflows:
        wf_id = wf.get("id")
        steps = wf.get("steps", [])
        ids = [get_step_id(s) for s in steps]

        # Check Order
        if "step_guard" in ids and "step_context" in ids:
            g_idx = ids.index("step_guard")
            c_idx = ids.index("step_context")

            if c_idx != g_idx + 1:
                print(f"[FAIL] {wf_id}: Order wrong. Context at {c_idx}, expected {g_idx+1}")
                errors += 1

            # Check Causal Position (Must be downstream of Context)
            if "step_causal" in ids:
                causal_idx = ids.index("step_causal")
                if causal_idx < c_idx:
                    print(f"[FAIL] {wf_id}: Logic Error! Causal ({causal_idx}) is before Context ({c_idx})")
                    errors += 1

                # Check 2: Lean Steps (Wiring Only)
                forbidden_keys = ["config", "task_key", "llm_prompts", "model_strategy"]
                for i, step in enumerate(steps):
                    if isinstance(step, dict):
                        for key in forbidden_keys:
                            if key in step:
                                print(f"[FAIL] {wf_id}: Step {i} ({step.get('id')}) contains forbidden definition key '{key}'. Define this in top-level 'steps' registry instead.")
                                errors += 1

                # Verify Reference Integrity (Is it in the Registry?)
                if "step_causal" not in registry_step_ids:
                     print(f"[FAIL] {wf_id}: step_causal referenced but NOT found in Registry (top-level steps)!")
                     errors += 1
                else:
                     pass # OK - Reference is valid

    if errors > 0:
        print(f"Verification FAILED with {errors} errors.")
        sys.exit(1)

    print("Verification SUCCESS: Context positioned correctly, Causal flow intact.")

if __name__ == "__main__":
    verify_final_state()
