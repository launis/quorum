import asyncio, os, sys
from datetime import datetime, UTC
sys.path.append('c:/src/quorum')

from backend.dependencies import get_async_repository

async def test():
    repo = await get_async_repository()
    
    # Let's see the actual executions in the DB
    execs = await repo.get_all_executions()
    print("All Executions:")
    now = datetime.now(UTC)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    print(f"Filter start_of_month: {start_of_month}")
    
    for e in execs:
        eid = getattr(e, "id", "N/A")
        completed_at = getattr(e, "completed_at", "N/A")
        print(f"ID: {eid}, completed_at: {completed_at}")
        
    res_sys = await repo.get_detailed_usage("system", None, start_of_month)
    print(f"Detailed Usage for System via Repo: {res_sys}")

if __name__ == "__main__":
    asyncio.run(test())
