import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.database.factory import get_repository
from backend.settings import get_settings

async def main():
    try:
        settings = get_settings()
        print(f"Settings DB Path: {settings.prod_db_path}")
        print(f"Active Backend: {settings.active_backend}")
        
        # force local if needed, but settings should match
        # settings.storage_backend = "LOCAL" 
        
        repo = await get_repository(settings)
        print(f"Repo Driver: {repo.driver}")
        
        items = await repo.get_knowledge_base_items()
        print(f"Items found via Repo: {len(items)}")
        
        if items:
            print(f"First item: {items[0]}")
        else:
            print("No items found.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
