"""Utility to verify database consistency across environments."""

import json
from pathlib import Path

FILES_TO_CHECK = [
    r"C:\src\quorum\backend\seed\seed_data.json",
    r"C:\src\quorum\backend\database\db_mock.json",
    r"C:\src\quorum\data\db.json"
]

def check_file(filepath):
    """Checks a specific database file for workflow counts and non-compliant names."""
    print(f"\n--- Checking {filepath} ---")
    path = Path(filepath)
    if not path.exists():
        print("FILE NOT FOUND")
        return

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # seed_data.json has "workflows": [...] (list)
        # db files usually have "workflows": {...} (dict) or list depending on implementation

        workflows = data.get("workflows")

        if isinstance(workflows, list):
            items = workflows
        elif isinstance(workflows, dict):
            items = workflows.values()
        else:
            print(f"Unknown workflows format: {type(workflows)}")
            return

        count = 0
        non_courtroom = []
        for wf in items:
            name = wf.get("name", "UNKNOWN")
            count += 1
            if not name.lower().startswith("courtroom"):
                non_courtroom.append(name)

        print(f"Total Workflows: {count}")
        if non_courtroom:
            print(f"!! WARNING !! Found {len(non_courtroom)} NON-COURTROOM workflows:")
            for name in non_courtroom:
                print(f"- {name}")
        else:
            print("OK: All workflows start with 'Courtroom'")

    except Exception as e:
        print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    for f in FILES_TO_CHECK:
        check_file(f)
