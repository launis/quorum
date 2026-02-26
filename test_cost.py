import asyncio, os, sys
sys.path.append('c:/src/quorum')

from backend.dependencies import get_async_repository

async def test():
    repo = await get_async_repository()
    execs = await repo.get_all_executions()
    print("Recent Executions:")
    for e in execs[-5:]:
        eid = getattr(e, 'id', e.get('id', 'N/A')) if isinstance(e, dict) else getattr(e, 'id', 'N/A')
        cost = getattr(e, 'cost_estimate', e.get('cost_estimate', 0.0)) if isinstance(e, dict) else getattr(e, 'cost_estimate', 0.0)
        status = getattr(e, 'status', e.get('status', 'N/A')) if isinstance(e, dict) else getattr(e, 'status', 'N/A')
        duration = getattr(e, 'duration_ms', e.get('duration_ms', 'N/A')) if isinstance(e, dict) else getattr(e, 'duration_ms', 'N/A')
        print(f"ID: {eid}, Cost: {cost}, Status: {status}, Duration: {duration}")
        
    orgs = await repo.list_organizations()
    for o in orgs:
        print(f"Org: {o.get('id')} - {o.get('name')}")
        agg = await repo.get_usage_aggregate("organization", o.get('id'), "2026-02")
        print(f"Agg: {agg}")

if __name__ == "__main__":
    asyncio.run(test())
