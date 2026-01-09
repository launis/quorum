import json

with open(r"c:\Users\risto\OneDrive\quorum\data\db.json", encoding="utf-8") as f:
    data = json.load(f)

workflows = data.get("workflows", {})
# TinyDB: if it's a dict (table), iterate values. If list (seed), iterate it.
if isinstance(workflows, dict):
    workflow_list = workflows.values()
else:
    workflow_list = workflows

for wf in workflow_list:
    if "Courtroom 3.0" in wf.get("name", ""):
        print(f"ID: {wf['id']}")
        print(f"Name: {wf['name']}")
        print(f"Org: {wf.get('organization_id')}")
        print(f"Public: {wf.get('is_public')}")
        print("-" * 20)
