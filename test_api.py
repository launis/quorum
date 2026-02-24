import json
import asyncio
from backend.database.tinydb_driver import TinyDBRepository
from backend.models.dtos.config import _component_adapter

async def main():
    repo = TinyDBRepository('data/db.json')
    raw = await repo.get_all_components(exclude_types=['agent', 'matrix', 'output_config'])
    print(f"Raw Components: {len(raw)}")
    
    valid = 0
    for c in raw:
        try:
            _component_adapter.validate_python(c)
            valid += 1
        except Exception as e:
            print(f"Failed ID: {c.get('id')} - {e}")
            
    print(f"Valid Components: {valid}")

asyncio.run(main())
