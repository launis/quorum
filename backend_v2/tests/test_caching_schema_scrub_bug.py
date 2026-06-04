import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend_v2.llm.client import LLMClient
from backend_v2.models.llm import LLMProviderConfig
from pydantic import BaseModel, Field

class MockSchema(BaseModel):
    blk_123: str = Field(description="Mock block")

@pytest.mark.asyncio
async def test_caching_schema_scrub_bug():
    """TDD Repro for Tier 4 Bug Hunting: schema instruction lost due to system message scrub."""
    
    # 1. Setup Mock Config
    config = LLMProviderConfig(
        id="prv_1234567890", 
        model_name="test_model", 
        provider="google", 
        tpm_limit=100000, 
        rpm_limit=100,
        parsing_mode="STRUCTURED_JSON"
    )
    
    client = LLMClient(config=config)
    
    # 2. Simulate raw inputs
    messages = [{"role": "user", "content": "Hello"}]
    
    # We want to see how the messages look AFTER client.py has manipulated them, but BEFORE provider.py
    # Wait, client.py passes final_messages to provider.generate()
    # We can mock LLMFactory.create_provider to capture the final_messages passed to it.
    
    mock_provider = AsyncMock()
    # Mock return so it doesn't crash on token_usage
    mock_response = MagicMock()
    mock_response.content = '{"blk_123": "value"}'
    mock_response.token_usage = {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
    mock_provider.generate.return_value = mock_response
    
    with patch("backend_v2.llm.client.LLMFactory.create_provider", return_value=mock_provider):
        await client.run_structured_task(
            messages=messages,
            response_model=MockSchema
        )
        
    # Capture the exact kwargs passed to generate()
    call_kwargs = mock_provider.generate.call_args.kwargs
    final_messages = call_kwargs.get("messages", [])
    
    # If the bug exists, client.py injected it as a SYSTEM message.
    # Our RED state test will assert that it is NOT a system message, meaning it fails BEFORE the fix.
    
    has_system_msg = any(msg.get("role") == "system" for msg in final_messages)
    
    # The fix should ensure the schema mandate is injected into a USER message.
    # So if has_system_msg is True, we fail the test to prove the bug exists.
    if has_system_msg:
        pytest.fail("BUG: Schema instruction was injected as a 'system' message, which will be scrubbed by provider.py!")
