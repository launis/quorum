
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.llm.provider import LiteLLMProvider, LLMResponse
from pydantic import BaseModel

class MockOutput(BaseModel):
    summary: str

@pytest.mark.asyncio
async def test_litellm_usage_extraction():
    """
    Verifies that LiteLLMProvider correctly extracts usage from Instructor's create_with_completion.
    """
    # Mock Usage Service
    mock_usage = AsyncMock()
    
    # Initialize Provider
    provider = LiteLLMProvider(
        model_name="mock-model",
        api_key="mock-key",
        usage_service=mock_usage,
        limits={"tpm": 1000, "rpm": 100}
    )
    
    # Mock Internal Client
    provider.client = MagicMock()
    provider.client.chat.completions.create_with_completion = AsyncMock()
    
    # Setup Mock Return Values
    mock_pydantic_obj = MockOutput(summary="Test Summary")
    
    mock_raw_response = MagicMock()
    mock_raw_response.usage.prompt_tokens = 150
    mock_raw_response.usage.completion_tokens = 50
    mock_raw_response.usage.total_tokens = 200
    mock_raw_response.model_dump.return_value = {"meta": "data"}
    
    # Return tuple (model, raw)
    provider.client.chat.completions.create_with_completion.return_value = (mock_pydantic_obj, mock_raw_response)
    
    # Execute
    response = await provider.generate(
        prompt="Test Prompt",
        response_schema=MockOutput,
        temperature=0.0,
        max_tokens=100
    )
    
    # Verify
    assert isinstance(response, LLMResponse)
    assert response.token_usage["prompt_tokens"] == 150
    assert response.token_usage["completion_tokens"] == 50
    assert response.token_usage["total_tokens"] == 200
    assert response.parsed_content["summary"] == "Test Summary"
    
    # Verify Usage Service Call (Cost calculation is usually done inside generate via litellm.completion_cost)
    # But since we mock the response, litellm.completion_cost might fail or return 0 if not mocked.
    # provider.py catches simple exceptions in usage tracking, so it might not crash.
