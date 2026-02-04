import json
import sys
from pathlib import Path


def verify_config():
    # Adjust path if running from root or scripts dir
    if Path("data/db.json").exists():
        db_path = Path("data/db.json")
    elif Path("../data/db.json").exists():
        db_path = Path("../data/db.json")
    else:
        print(f"Error: data/db.json not found in {Path.cwd()}")
        sys.exit(1)

    print(f"Loading database from: {db_path.absolute()}")
    try:
        with open(db_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)

    workflows = data.get("workflows", {})
    issues = []

    print(f"\nScanning {len(workflows)} workflows for Strict Mode compliance (temperature & max_tokens)...")

    for wf_id, wf in workflows.items():
        step_count = len(wf.get("steps", []))
        print(f"Checking Workflow: {wf.get('name', wf_id)} ({step_count} steps)")

        for step in wf.get("steps", []):
            step_id = step.get("id", "unknown_step")
            config = step.get("config", {})

            temp = config.get("temperature")
            tokens = config.get("max_tokens")

            # Strict check: Must not be None. 0.0 is valid for temp.
            if temp is None:
                issues.append(f"VIOLATION: Workflow '{wf_id}' / Step '{step_id}' -> Missing 'temperature'")
            if tokens is None:
                issues.append(f"VIOLATION: Workflow '{wf_id}' / Step '{step_id}' -> Missing 'max_tokens'")

    if issues:
        print("\n❌ VALIDATION FAILED:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION SUCCESS: All 100% of workflow steps have Strict Mode configuration.")
        sys.exit(0)

if __name__ == "__main__":
    verify_config()
