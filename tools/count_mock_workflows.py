"""Utility to counting mock workflows in the database."""

import json

DB_FILE = r"C:\src\quorum\backend\database\db_mock.json"

try:
    with open(DB_FILE, encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", {})
    print(f"Total Workflows in DB: {len(workflows)}")
    for _, wf in workflows.items():
        print(f"- {wf.get('name')}")

except Exception as e:
    print(f"Error: {e}")
