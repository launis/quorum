import json

DB_FILE = r"C:\src\quorum\backend\database\db_mock.json"

try:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    workflows = data.get("workflows", {})
    print(f"Total Workflows in DB: {len(workflows)}")
    for wf_id, wf in workflows.items():
        print(f"- {wf.get('name')}")

except Exception as e:
    print(f"Error: {e}")
