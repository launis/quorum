
import asyncio
from backend.database.wrapper import get_db_client
from backend.database.repository import TinyDBRepository
from backend.models.auth import Organization
from backend.api.organization_router import OrganizationResponse

async def debug_validation():
    print("--- DEBUG MODEL VALIDATION ---")
    
    # 1. Setup Repo
    db = get_db_client()
    repo = TinyDBRepository(db)
    
    # 2. List items
    items = await repo.list_organizations()
    print(f"Found {len(items)} items in DB.")
    
    for i, item in enumerate(items):
        print(f"\nItem {i} Raw Dict: {item}")
        
        # 3. Wrap in Organization
        try:
            org = Organization(**item)
            print(f"  -> Organization Object: {org}")
            print(f"  -> Dump: {org.model_dump()}")
        except Exception as e:
            print(f"  FAILED to create Organization: {e}")
            continue
            
        # 4. Wrap in Response
        try:
            resp = OrganizationResponse(**org.model_dump())
            print(f"  -> OrganizationResponse: {resp}")
        except Exception as e:
            print(f"  FAILED to create Response: {e}")

if __name__ == "__main__":
    asyncio.run(debug_validation())
