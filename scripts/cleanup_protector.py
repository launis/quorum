
import json
import os

DB_PATH = "backend/database/db_mock.json"

def clean_protector():
    if not os.path.exists(DB_PATH):
        print(f"File not found: {DB_PATH}")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", {})
    to_delete = []

    for wf_id, wf in workflows.items():
        if wf.get("name") == "Protector":
            to_delete.append(wf_id)

    if not to_delete:
        print("No 'Protector' workflows found.")
        return

    print(f"Found {len(to_delete)} 'Protector' workflows to delete: {to_delete}")
    
    for wf_id in to_delete:
        del workflows[wf_id]

    data["workflows"] = workflows

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("Cleanup complete.")

if __name__ == "__main__":
    clean_protector()
