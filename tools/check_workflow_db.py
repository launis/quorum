
import json
import sys

DB_PATH = "c:/Users/risto/OneDrive/quorum/data/db.json"
WORKFLOW_ID = "wf-courtroom-2-0-dual-matrix-6685039d"

def check_workflow():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        workflows = data.get('workflows', {})
        # workflows might be a list or a dict in TinyDB depending on how it's stored.
        # In seed_data.json it was a list. In TinyDB, it's usually a dict where keys are document IDs (integers).
        
        target_workflow = None
        
        if isinstance(workflows, dict):
            for key, wf in workflows.items():
                if wf.get('id') == WORKFLOW_ID:
                    target_workflow = wf
                    break
        elif isinstance(workflows, list):
             for wf in workflows:
                if wf.get('id') == WORKFLOW_ID:
                    target_workflow = wf
                    break
        
        if target_workflow:
            print(f"Found workflow: {target_workflow['name']}")
            print("Steps configured:")
            print(json.dumps(target_workflow.get('steps', []), indent=2))
        else:
            print(f"Workflow with ID {WORKFLOW_ID} NOT FOUND in {DB_PATH}")

    except Exception as e:
        print(f"Error reading DB: {e}")

if __name__ == "__main__":
    check_workflow()
