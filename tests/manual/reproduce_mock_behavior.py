
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.llm.provider import LLMFactory, MockProvider, LiteLLMProvider
from backend.settings import get_settings

async def main():
    print("--- Verifying LLMFactory Behavior with USE_MOCK_LLM=True ---")
    
    # 1. Force USE_MOCK_LLM = True at runtime environment level
    # Note: Pydantic settings load from env, so we need to mock the settings or env before instantiation if possible.
    # But get_settings() is cached. We might need to reload or manually inspect the factory logic.
    os.environ["USE_MOCK_LLM"] = "true"
    
    # Reload settings to ensure env var is picked up (if strictly following code)
    # or just trust the factory logic we read.
    # LLMFactory checks provider_type arg, not settings for the decision (mostly).
    
    settings = get_settings()
    # Manually override for this test if cache prevents update
    settings.use_mock_llm = True
    print(f"Settings.use_mock_llm: {settings.use_mock_llm}")

    # 2. Request 'vertex_ai' provider
    provider_type = "vertex_ai"
    model_name = "gemini-1.5-pro"
    
    print(f"Requesting provider: '{provider_type}' with model: '{model_name}'")
    
    try:
        provider = LLMFactory.create_provider(
            provider_type=provider_type,
            model_name=model_name
        )
        
        print(f"Provider created: {type(provider).__name__}")
        
        if isinstance(provider, MockProvider):
            print("SUCCESS: MockProvider returned.")
        elif isinstance(provider, LiteLLMProvider):
            print("FAILURE: LiteLLMProvider returned (Silent override NOT active).")
            # Expected behavior based on code reading is FAILURE.
            
    except Exception as e:
        print(f"Exception during provider creation: {e}")

    # 3. Request 'mock' provider
    provider_type_mock = "mock"
    print(f"\nRequesting provider: '{provider_type_mock}'")
    provider_mock = LLMFactory.create_provider(provider_type=provider_type_mock, model_name="mock-model")
    print(f"Provider created: {type(provider_mock).__name__}")

if __name__ == "__main__":
    asyncio.run(main())
