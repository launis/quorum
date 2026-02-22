import asyncio
import logging
import sys

# Add project root to path
sys.path.append("c:/src/quorum")

from backend.database.factory import get_repository
from backend.database.wrapper import get_db_client
from backend.services.agent_registry import AgentRegistry
from backend.settings import get_settings

# Mock logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_strategies():
    print("--- Verifying Dynamic Strategies ---")

    # 1. Initialize Registry
    repo = await get_repository(get_settings(), get_db_client())
    registry = AgentRegistry(repo)

    # 2. Test get_all_strategies
    print("\n[1] Fetching All Strategies...")
    try:
        strategies = await registry.get_all_strategies()
        print(f"Found {len(strategies)} strategies:")
        for key, model in strategies.items():
            print(f"  - {key}: {model}")

        # 3. Simulate Suffix Logic
        print("\n[2] Simulating Suffix Logic...")
        display_strategies = {k: v for k, v in strategies.items() if k.islower()}

        # Test cases based on seed_data.json knowledge
        test_cases = [
            "vertex_ai/gemini-2.5-flash",  # mapped to strict, fast
            "vertex_ai/gemini-2.5-pro",  # mapped to deep, precise
            "vertex_ai/unknown-model",  # no map
        ]

        for current_model in test_cases:
            model_display = current_model
            suffix = ""
            # Sorted iteration as implemented in agents_router.py
            for s_key in sorted(display_strategies.keys()):
                s_resolved = display_strategies[s_key]
                if current_model == s_resolved:
                    suffix = f" ({s_key.capitalize()})"
                    model_display = f"{current_model}{suffix}"
                    break

            print(f"  '{current_model}' -> '{model_display}'")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()

    print("\n--- Verification Complete ---")


if __name__ == "__main__":
    asyncio.run(verify_strategies())
