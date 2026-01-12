"""Utility to inspect seed data."""

import json

try:
    with open(r"C:\src\quorum\backend\seed\seed_data.json", encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", [])
    for wf in workflows:
        if "audit" in wf.get("id", "").lower() or "audit" in wf.get("name", "").lower():
            print(f"--- Workflow: {wf.get('name')} ({wf.get('id')}) ---")
            ui_schema = wf.get("ui_schema", {})
            print("Inputs defined in UI Schema:")
            for key, val in ui_schema.items():
                print(f"  Key: {key}")
                print(f"    Type: {val.get('ui:widget', 'default')} / {val.get('ui:options', {}).get('accept', 'N/A')}")
            print("\n")
except Exception as e:
    print(f"Error: {e}")
