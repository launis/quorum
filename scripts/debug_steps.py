import asyncio

from backend.core.settings import get_settings
from backend.database.factory import get_repository


async def main():
    settings = get_settings()
    repo = get_repository(settings)

    # 1. Inspect the workflow
    wf = await repo.get_workflow_definition("ca09d8a4-a694-4aab-95d0-770535d44f85")
    if not wf:
        print("Workflow not found!")
        return

    print(f"Workflow found: {wf.name}")
    print(f"Steps: {wf.steps}")

    # 2. Inspect first step
    for step_id in wf.steps[:3]:
        step = await repo.get_step_by_id(step_id)
        if step:
            print(f"[{step_id}] -> name: {step.get('name')}, slug: {step.get('slug')}")
        else:
            print(f"[{step_id}] -> NOT FOUND")

if __name__ == "__main__":
    asyncio.run(main())
