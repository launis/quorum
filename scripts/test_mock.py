import asyncio
from unittest.mock import AsyncMock

async def main():
    m = AsyncMock()
    m.foo.return_value = 5
    res = await m.foo()
    print("Result:", res)
    print("Type:", type(res))

if __name__ == "__main__":
    asyncio.run(main())
