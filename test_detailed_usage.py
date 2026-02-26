import asyncio, os, sys
sys.path.append('c:/src/quorum')

from backend.dependencies import get_async_repository

async def test():
    repo = await get_async_repository()
    
    # Test detailed usage for Demo Corp
    res = await repo.get_detailed_usage("org", "f86ec3f7-8920-4cf2-bf33-bb53b8651070", "2026-02-01T00:00:00")
    print(f"Detailed Usage for Demo Corp: {res}")
    
    # Test for System
    res_sys = await repo.get_detailed_usage("system", None, "2026-02-01T00:00:00")
    print(f"Detailed Usage for System: {res_sys}")

if __name__ == "__main__":
    asyncio.run(test())
