
import asyncio
import os
import sys
import traceback

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.getcwd())

async def verify():
    print("Starting verification...")
    try:
        from backend.database.repository import TinyDBRepository
        from backend.models.workflow import WorkflowDefinition
        print("Imports OK")

        db_path = "c:/src/quorum/data/db.json"
        print(f"Loading DB from: {db_path}")
        
        repo = TinyDBRepository(db_path)
        print("Repository initialized")
        
        workflow_id = "sequential_audit_chain"
        print(f"Fetching workflow: {workflow_id}...")
        
        try:
            wf = await repo.get_workflow_definition(workflow_id)
            print("get_workflow_definition returned")
        except Exception as e:
            print(f"get_workflow_definition FAILED: {e}")
            traceback.print_exc()
            return

        if not wf:
            print("Workflow not found!")
            return

        print(f"Workflow Loaded: {wf.name}")
        print(f"Steps count: {len(wf.steps)}")
        
        missing_keys = []
        for i, step in enumerate(wf.steps):
            if not step.task_key:
                missing_keys.append(f"Step {i} ({step.id})")
            else:
                pass 
                # print(f"  Step {i}: {step.id} -> task_key={step.task_key}")
                
        if missing_keys:
            print(f"FAILURE: Missing task_key in: {missing_keys}")
        else:
            print("SUCCESS: All steps have task_key.")

    except Exception as e:
        print(f"CRITICAL ERROR in verify(): {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(verify())
    except Exception as e:
         print(f"CRITICAL ERROR in main: {e}")
         traceback.print_exc()
