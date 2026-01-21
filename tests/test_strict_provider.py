
import os
os.environ["USE_MOCK_LLM"] = "true"

import pytest
from backend.llm.provider import MockProvider
from backend.exceptions import ConfigurationError

@pytest.mark.asyncio
async def test_strict_provider_enforcement():
    """Verify that MockProvider rejects implicit defaults."""
    
    # Instantiate provider (Mock is simpler)
    provider = MockProvider(
        model_name="mock-model",
        # Mock doesn't need API keys or Env vars usually
    )
    

    # 1. Test Missing Temperature
    print("STEP 1: Testing Missing Temperature")
    try:
        await provider.generate(
            prompt="Hello",
            max_tokens=100
            # temperature missing
        )
        print("FAIL: Step 1 did not raise exception")
        raise Exception("Step 1 Failed: No exception raised")
    except ConfigurationError as e:
        print(f"STEP 1: Caught expected error: {e}")
        if "Strict Mode: 'temperature'" not in str(e):
             print(f"FAIL: Step 1 wrong message: {e}")
             raise e
        print("STEP 1: SUCCESS")

    # 2. Test Missing Max Tokens
    print("STEP 2: Testing Missing Max Tokens")
    try:
        await provider.generate(
            prompt="Hello",
            temperature=0.5
            # max_tokens missing
        )
        print("FAIL: Step 2 did not raise exception")
        raise Exception("Step 2 Failed: No exception raised")
    except ConfigurationError as e:
        print(f"STEP 2: Caught expected error: {e}")
        if "Strict Mode: 'max_tokens'" not in str(e):
             print(f"FAIL: Step 2 wrong message: {e}")
             raise e
        print("STEP 2: SUCCESS")
    
    # 3. Test Success with All Params
    print("STEP 3: Testing Success Case")
    try:
        await provider.generate(
            prompt="Hello",
            temperature=0.5,
            max_tokens=100
        )
        print("STEP 3: SUCCESS")
    except Exception as e:
        print(f"FAIL: Step 3 raised exception: {e}")
        raise e

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_strict_provider_enforcement())
        print("SUCCESS: All strict checks passed")
    except Exception as e:
        print(f"FAIL: Test script failed: {e}")
