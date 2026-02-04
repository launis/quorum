from tinydb import TinyDB, Query

def fix_workflow_db():
    try:
        db = TinyDB('c:/src/quorum/data/db.json')
        workflows_table = db.table('workflows')
        
        print("Scanning Workflows for corrupted steps...")
        Workflow = Query()
        
        for wf in workflows_table.all():
            steps = wf.get('steps', [])
            if not isinstance(steps, list): continue
            
            modified = False
            for step in steps:
                if isinstance(step, dict):
                    # Check for null task_key
                    if step.get('task_key') is None:
                        print(f"FIXING: Workflow '{wf.get('id')}' -> Step '{step.get('id')}' has NULL task_key. Setting to 'unknown'.")
                        step['task_key'] = 'unknown'
                        modified = True
                        
            if modified:
                print(f"Applying fix to Workflow '{wf.get('id')}'...")
                workflows_table.update({'steps': steps}, Workflow.id == wf.get('id'))
                print("Update successful.")
        
        print("Scan complete.")

    except Exception as e:
        print(f"Error updating DB: {e}")

if __name__ == "__main__":
    fix_workflow_db()
