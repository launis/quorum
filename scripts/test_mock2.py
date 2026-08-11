import asyncio
from unittest.mock import AsyncMock

async def main():
    m = AsyncMock()
    m.get_workflow.return_value = {"id": "test"}
    res = await m.get_workflow(workflow_id="wf_123")
    print("Result:", res)
    print("Type:", type(res))

if __name__ == "__main__":
    asyncio.run(main())
