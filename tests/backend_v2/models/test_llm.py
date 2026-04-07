import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.llm import LLMProviderConfig, LLMResponse


def test_llm_provider_config_valid() -> None:
    """Test valid instantiation of LLMProviderConfig."""
    config = LLMProviderConfig(
        id="vertex_ai/gemini-pro",
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


def test_llm_provider_config_invalid() -> None:
    """Test validation constraints on LLMProviderConfig."""
    with pytest.raises(AppException) as exc_info:
        LLMProviderConfig(
            id="",  # Empty string should fail
            provider="vertex_ai",
            model_name="gemini-pro",
            tpm_limit=1000,
            rpm_limit=100,
        )
    assert exc_info.value.status_code == 422


def test_llm_response_valid() -> None:
    """Test valid instantiation of LLMResponse."""
    response = LLMResponse(
        content="Success",
        token_usage={"prompt_tokens": 10},
    )
    assert response.content == "Success"
