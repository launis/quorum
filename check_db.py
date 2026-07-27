import asyncio
from backend_v2.database.factory import get_driver
from backend_v2.settings import get_settings
from backend_v2.database.repository import UnifiedWorkflowRepository

async def main():
    driver = await get_driver(get_settings())
    repo = UnifiedWorkflowRepository(driver)
    p_dict = await repo.get_output_profile_by_id("prf_5d6e7f8091a2b3c4")
    print("content_blocks length:", len(p_dict.get('content_blocks', [])))
    import json
    print(json.dumps(p_dict.get('content_blocks', []), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
