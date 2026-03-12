import json
from pathlib import Path


def main():
    seed_path = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
    if not seed_path.exists():
        print(f"Error: Could not find {seed_path}")
        return

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", [])

    for workflow in workflows:
        print(f"Processing workflow: {workflow.get('id')}")
        steps = workflow.get("steps", [])

        # Build mapping from old node ID to new semantic ID
        id_mapping = {}
        for step in steps:
            old_id = step.get("id")
            blueprint = step.get("task_blueprint")
            if old_id and blueprint and old_id != blueprint:
                # Based on the plan, if blueprint is step_analyst, the new id should be step_analyst itself.
                # However we need to make sure we don't have clashing IDs within a single workflow.
                # In Courtroom 2.0, all blueprints are used exactly once.
                new_id = blueprint
                id_mapping[old_id] = new_id

        if not id_mapping:
            print("No steps needed refactoring in this workflow.")
            continue

        print(f"ID Mapping: {id_mapping}")

        # Apply the mapping
        for step in steps:
            # 1. Update ID
            old_id = step.get("id")
            if old_id in id_mapping:
                step["id"] = id_mapping[old_id]

            # 2. Update depends_on
            depends_on = step.get("depends_on", [])
            new_depends_on = [id_mapping.get(dep, dep) for dep in depends_on]
            step["depends_on"] = new_depends_on

            # 3. Update input_mappings
            input_mappings = step.get("input_mappings", {})
            new_mappings = {}
            for key, val in input_mappings.items():
                new_key = key
                new_val = val

                # The old input_mappings keys were typically blueprint names (e.g. "step_analyst")
                # But sometimes it might be the old node ID. Let's map both.
                if key in id_mapping:
                    new_key = id_mapping[key]

                # Fix ".output" bug -> "$<new_id>"
                # If the value is exactly ".output" and the key corresponds to a dependent step
                if val == ".output":
                    # Since the key is already the step name (like "step_analyst" or "step_guard"),
                    # we should refer to it as "$step_analyst".
                    # If the key was changed, use the new key.
                    # As defined in the plan: "step_analyst": ".output" -> "step_analyst": "$step_analyst"
                    new_val = f"${new_key}"
                elif val.startswith("."):
                    # generic fallback if there was something else like .some_other_field
                    new_val = f"${new_key}{val}"

                new_mappings[new_key] = new_val

            step["input_mappings"] = new_mappings

    # Write back to file
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        # Add a trailing newline the way IDEs typically do
        f.write("\n")

    print("Successfully refactored seed_data.json")

if __name__ == "__main__":
    main()
