import asyncio
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from backend.database.factory import get_repository
from backend.settings import get_settings

async def main():
    try:
        settings = get_settings()
        repo = await get_repository(settings)
        
        items = await repo.get_knowledge_base_items()
        with open("db_sample.txt", "w", encoding="utf-8") as f:
            f.write(f"Total Items in DB: {len(items)}\n")
            
            types = {}
            for item in items:
                t = item.get("type")
                if t not in types:
                    types[t] = []
                types[t].append(item)
                
            f.write("\n=== SAMPLE DATA ===\n")
            
            for t, list_items in types.items():
                f.write(f"\n--- TYPE: {t.upper()} (Count: {len(list_items)}) ---\n")
                if list_items:
                    sample = list_items[0]
                    f.write(json.dumps(sample, indent=2, default=str))
                    f.write("\n")


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
