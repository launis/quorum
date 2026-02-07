
import asyncio
import os
import sys

# Add path
sys.path.append(os.getcwd())

from backend.database.repository import TinyDBRepository

async def main():
    try:
        repo = TinyDBRepository("c:/src/quorum/data/db.json")
        wf = await repo.get_workflow_definition("sequential_audit_chain")
        print("Success")
        if wf:
            print(f"Name: {wf.name}")
            print(f"Steps: {len(wf.steps)}")
        else:
            print("Workflow is None")
    except Exception:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
