
import json
import os

SEED_FILE = r"c:\src\quorum\backend\seed\seed_data.json"

# Mapping from Step ID to Registry Task Key
KEY_MAPPING = {
    "step_guard": "guard",
    "step_analyst": "analyst",
    "step_interaction": "interaction",
    "step_profiler": "profiler",
    "step_panel": "panel",
    "step_archivist": "archivist",
    "step_judge": "judge",
    "step_coach": "coach",
    "step_context": "retrieve_context",
    "step_xai": "xai",
    "step_logician": "logician",
    "step_falsifier": "falsifier",
    "step_overseer": "overseer",
    "step_causal": "causal",
    "step_detector": "detector"  # Assuming 'detector' from context, will verify in critique.py
}

def patch_seed_data():
    if not os.path.exists(SEED_FILE):
        print(f"Error: {SEED_FILE} not found.")
        return

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    
    # Traverse the JSON. Structure is usually list of objects.
    # We look for "steps" list in workflow definitions.
    
    # Strategy: Recursive search for "steps" list or check if items in a list look like steps.
    # From previous views, seed_data.json seems to be a list of workflows/components?
    # Or a dict with keys? Let's assume it's a list based on "steps.0.task_key" error which implies validation on a model.
    # Actually the error "10 validation errors for WorkflowDefinition" suggests we are validating Workflow definitions.
    
    def process_node(node):
        nonlocal updated_count
        if isinstance(node, dict):
            # If this node has "steps" and it's a list, iterate it
            if "steps" in node and isinstance(node["steps"], list):
                for step in node["steps"]:
                    if isinstance(step, dict) and "id" in step:
                        step_id = step["id"]
                        if "task_key" not in step:
                            # Try to find a match
                            if step_id in KEY_MAPPING:
                                step["task_key"] = KEY_MAPPING[step_id]
                                updated_count += 1
                                print(f"Patching step {step_id} -> {KEY_MAPPING[step_id]}")
            
            # Recurse
            for key, value in node.items():
                process_node(value)
        elif isinstance(node, list):
            for item in node:
                process_node(item)

    process_node(data)
    
    if updated_count > 0:
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully patched {updated_count} steps in seed_data.json")
    else:
        print("No steps needed patching.")

if __name__ == "__main__":
    patch_seed_data()
