
import asyncio
import logging

from backend.agents.guard import GuardAgent
from backend.models.state import WorkflowState

# Setup minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_guard_validation():
    print("--- Starting Verify Guard Schema Validation ---")

    # 1. Setup State with Banned Phrases
    state = WorkflowState(
        inputs={
            "history_text": "This is a clean history.",
            "product_text": "This text contains forbidden magic_word.",
            "reflection_text": "Reflection is clean."
        },
        aux_data={
            "banned_phrases": ["magic_word", "secret_code"]
        }
    )

    agent = GuardAgent()

    # 2. Trigger Pre-Hook (prepare_context) where validation happens
    print("[Test] Calling prepare_context (should fail)...")
    try:
        await agent.prepare_context(state)
        print("[FAILURE] Validation did NOT raise exception for banned phrase.")
    except Exception as e:
        print(f"[SUCCESS] Caught expected exception: {e}")
        if "SECURITY_BANNED_PHRASE_DETECTED" in str(e):
             print("[SUCCESS] Error code matches protocol.")
        else:
             print(f"[WARNING] Error code mismatch. Got: {e}")

    # 3. Clean Test
    print("\n[Test] Testing clean input...")
    state.inputs.product_text = "This text is clean."
    try:
        await agent.prepare_context(state)
        print("[SUCCESS] Clean input passed validation.")
    except Exception as e:
         print(f"[FAILURE] Clean input raised exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_guard_validation())
