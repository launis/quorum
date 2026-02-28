import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.llm.provider import LiteLLMProvider
from backend.exceptions import AppException, ErrorCodes
from backend.models.llm import LLMProviderConfig

import instructor

@pytest.mark.asyncio
async def test_lite_llm_provider_fail_fast_parsing():
    """Test that LiteLLMProvider catches instructor ResponseParsingError and throws AppException."""
    
    # Note: We need a valid dummy config to initialize the provider
    config = MagicMock()
    config.model_name = "gemini-2.5-flash"
    config.api_key = "fake_key"
    config.tpm = 1000
    config.rpm = 10
    config.parsing_mode = None
    config.default_safety_settings = []
    config.vertex_location = "us-central1"
    config.supports_grounding = False

    # We mock Router and Instructor entirely to avoid real network/setup overhead
    with patch('backend.llm.provider.Router'), patch('backend.llm.provider.instructor.from_litellm'):
        provider = LiteLLMProvider(
            model_name="gemini-test", 
            api_key="fake",
            settings=config,
            limits={"tpm": 1000, "rpm": 10}
        )

        # Force the instructor client to raise a simulated Parsing/Empty Choices error
        class ResponseParsingError(Exception):
            pass
        async def fake_create(*args, **kwargs):
            raise ResponseParsingError("No completion choices found in LLM response")
            
        provider.client.chat.completions.create = fake_create
        
        async def fake_acompletion(*args, **kwargs):
            raise ResponseParsingError("No completion choices found in LLM response")
        provider.router.acompletion = fake_acompletion
        
        from pydantic import BaseModel
        class MockSchema(BaseModel):
            pass

        # Environment mocking for vertex_location
        with patch('os.getenv', return_value="us-central1"):
             # Execute generate. We expect it to raise AppException with AGENT_RESPONSE_PARSING_FAILED
             with pytest.raises(AppException) as excinfo:
                 # Remove the retry so the Exception bubbles up immediately
                 await provider.generate.__wrapped__(
                      provider, prompt="Test prompt", response_schema=MockSchema, temperature=0.5, max_tokens=100
                 )
                     
             # Verify it's translated to our standard AppException
             assert excinfo.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_PARSING_FAILED
             assert "Tekoälymalli palautti tyhjän tai virheellisesti muotoillun vastauksen" in excinfo.value.message
