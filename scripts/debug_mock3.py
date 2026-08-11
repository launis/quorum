import asyncio
from unittest.mock import AsyncMock

async def main():
    repo = AsyncMock()
    repo.get_workflow.return_value = {"id": "test"}
    print(await repo.get_workflow())

if __name__ == "__main__":
    asyncio.run(main())
