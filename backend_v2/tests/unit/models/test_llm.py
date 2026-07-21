from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.llm import LLMProviderConfig, LLMResponse


@pytest.mark.skip("Legacy architecture obsolete")
def test_llm_provider_config_valid() -> None:
    """Test valid instantiation of LLMProviderConfig."""
    config = LLMProviderConfig(
        id="prv_vertexai123",
        provider="vertex_ai",
        model_name="gemini-pro",
        api_key="secret",
        temperature=0.0,
        top_p=0.1,
        top_k=1,
        tpm_limit=1000,
        rpm_limit=100,
    )
    assert config.temperature == 0.0
    assert config.top_p == 0.1
    assert config.top_k == 1


@pytest.mark.skip("Legacy architecture obsolete")
def test_llm_provider_config_invalid() -> None:
    """Test validation constraints on LLMProviderConfig."""
    with pytest.raises(ValidationError) as exc_info:
        LLMProviderConfig(
            id="",  # Empty string should fail
            provider="vertex_ai",
            model_name="gemini-pro",
            tpm_limit=1000,
            rpm_limit=100,
        )
    assert exc_info.value.error_count() >= 1


@pytest.mark.skip("Legacy architecture obsolete")
def test_llm_response_valid() -> None:
    """Test valid instantiation of LLMResponse."""
    response = LLMResponse(
        content="Success",
        token_usage=TokenUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10),
    )
    assert response.content == "Success"
