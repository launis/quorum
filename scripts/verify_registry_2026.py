
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database.repository import TinyDBClient, TinyDBRepository
from backend.services.agent_registry import AgentRegistry


async def main():
    print("--- Verifying Strategy Resolution ---")

    # 1. Setup Repo (Mock/TinyDB)
    # We use the path where the code looks for it, or just in-memory if we rely on the hardcoded default in `get_model_registry`
    # In `repository.py`, `get_model_registry` currently has a hardcoded return for TinyDB mode!
    # So we don't even need a real DB file to test that method's logic if we use TinyDBRepository.

    # But wait, did I modify the hardcoded dict? Yes, I did.

    client = TinyDBClient("dummy_path") # won't write if we don't insert
    repo = TinyDBRepository(client)

    registry = AgentRegistry(repo)

    # 2. Resolve 'deep'
    try:
        config = await registry.resolve_model_config("deep")
        print(f"Strategy 'deep' resolved to: {config}")

        if config['model_name'] == "gemini-2.5-pro":
            print("SUCCESS: Resolved to gemini-2.5-pro")
        else:
            print(f"FAILURE: Expected gemini-2.5-pro, got {config['model_name']}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
