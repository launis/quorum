import json
from pathlib import Path


def verify_judge_inputs():
    db_path = Path("c:/src/quorum/data/db.json")
    if not db_path.exists():
        print(f"Error: {db_path} not found.")
        return

    try:
        with open(db_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    workflows = data.get("workflows", {})

    # Normalize workflow list
    workflow_list = []
    if isinstance(workflows, dict):
        workflow_list = list(workflows.values())
    elif isinstance(workflows, list):
        workflow_list = workflows

    with open("audit_report.txt", "w", encoding="utf-8") as out:

        def log(msg):
            print(msg)
            out.write(msg + "\n")

        log(f"Scanning {len(workflow_list)} workflows...")

        judges = ["step_judge", "step_judge_cognitive"]
        global_pass = True

        for wf in workflow_list:
            wf_id = wf.get("id")
            wf_name = wf.get("name", "Unknown")
            log(f"\nChecking Workflow: {wf_name} ({wf_id})")

            steps = wf.get("steps", [])
            workflow_step_ids = {s.get("id") for s in steps}

            for step in steps:
                step_id = step.get("id")
                if step_id in judges:
                    config = step.get("config", {})
                    monitored_steps = config.get("monitored_steps", {})
                    inputs = step.get("inputs", {})
                    missing = []

                    # Check 1: Does it match monitored_steps config?
                    if monitored_steps:
                        for key in monitored_steps.keys():
                            if key not in inputs:
                                missing.append(f"{key} (from monitored_steps)")

                    # Check 2: hardcoded expectation
                    known_critics = [
                        "step_profiler",
                        "step_logician",
                        "step_falsifier",
                        "step_causal",
                        "step_detector",
                        "step_overseer",
                        "step_archivist",
                        "step_panel",
                    ]

                    for critic in known_critics:
                        if critic in workflow_step_ids:
                            if critic not in inputs:
                                if f"{critic} (from monitored_steps)" not in missing:
                                    missing.append(f"{critic} (available in workflow but missing in inputs)")

                    if missing:
                        log(f"  [FAIL] Step '{step_id}' missing inputs: {missing}")
                        global_pass = False
                    else:
                        log(f"  [PASS] Step '{step_id}' inputs OK.")

        if global_pass:
            log("\nSUCCESS: All Judge inputs are correctly configured across all workflows.")
        else:
            log("\nFAILURE: Some workflows have missing Judge inputs.")


if __name__ == "__main__":
    verify_judge_inputs()

if __name__ == "__main__":
    verify_judge_inputs()
