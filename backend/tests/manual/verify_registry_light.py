import asyncio
import logging
import sys

# Add project root to path
sys.path.append("c:/src/quorum")

from backend.database.factory import get_repository
from backend.database.wrapper import get_db_client
from backend.services.agent_registry import AgentRegistry
from backend.settings import get_settings

# Minimal Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY")


async def verify():
    print("--- Light Verification ---")
    try:
        repo = await get_repository(get_settings(), get_db_client())
        registry = AgentRegistry(repo)

        # Test 1: Fetch Strategies
        strategies = await registry.get_all_strategies()
        print(f"Strategies found: {len(strategies)}")
        for k, v in strategies.items():
            print(f"  {k} -> {v}")

        # Test 2: Resolve specific
        if "fast" in strategies:
            resolved = await registry.resolve_model_name("fast")
            print(f"Resolving 'fast' -> {resolved}")
        else:
            print("Warning: 'fast' strategy not found in DB.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(verify())
