import sys
import os
import asyncio
sys.path.insert(0, os.getcwd())

from backend_v2.settings import get_settings
from backend_v2.database.factory import get_repository
from backend_v2.services.blueprint import BlueprintTransformer

async def main():
    settings = get_settings()
    repo = await get_repository(settings)
    transformer = BlueprintTransformer(repo)
    dto = await transformer.build_report_dto("exe_4e7a8cbed1f2412c83ffae4b5d973318", "default", "fi")
    print(dto.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
