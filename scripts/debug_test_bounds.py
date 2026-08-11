import asyncio
from unittest.mock import AsyncMock
from backend_v2.tests.unit.test_llm_context_bounds import mock_repo, _create_workflow

async def main():
    repo = mock_repo()
    workflow_dict = await repo.get_workflow(workflow_id="wf_0000000000000000")
    print("Type of workflow_dict:", type(workflow_dict))
    print("Value:", workflow_dict)

if __name__ == "__main__":
    asyncio.run(main())
