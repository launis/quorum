
import json
import os

SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"
WORKFLOWS_PATH = r"c:\src\quorum\backend\seed\recovered_workflows.json"

def merge_workflows():
    if not os.path.exists(SEED_PATH):
        print(f"Seed file not found: {SEED_PATH}")
        return

    if not os.path.exists(WORKFLOWS_PATH):
        print(f"Workflows file not found: {WORKFLOWS_PATH}")
        return

    print("Reading seed data...")
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    print("Reading recovered workflows...")
    with open(WORKFLOWS_PATH, 'r', encoding='utf-16') as f: # PowerShell ConvertTo-Json uses UTF-16 by default usually, or we check encoding
        try:
             workflows = json.load(f)
        except json.JSONDecodeError:
             # Try utf-8 if utf-16 fails
             f.close()
             with open(WORKFLOWS_PATH, 'r', encoding='utf-8') as f2:
                 workflows = json.load(f2)
    
    # Handle PowerShell wrapper if present
    if isinstance(workflows, str):
        print("Workflows loaded as string, parsing...")
        workflows = json.loads(workflows)
        
    print(f"Found {len(workflows)} workflows to merge.")
    
    seed_data["workflows"] = workflows
    
    print("Writing merged data...")
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
    print("Merge complete.")

if __name__ == "__main__":
    merge_workflows()
