"""Unit tests for LLM schema models (LLMResponse, LLMProviderConfig, LLMMessageDTO, AdHoc models)."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.llm import (
    AdHocTestRequest,
    AdHocTestResponse,
    LLMMessageDTO,
    LLMProviderConfig,
    LLMResponse,
    ProviderMetadataDTO,
)


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
        frequency_penalty=0.5,
        presence_penalty=-0.5,
    )
    assert config.temperature == 0.0
    assert config.top_p == 0.1
    assert config.top_k == 1
    assert config.frequency_penalty == 0.5
    assert config.presence_penalty == -0.5


def test_llm_provider_config_invalid() -> None:
    """Test validation constraints on LLMProviderConfig."""
    with pytest.raises(ValidationError):
        LLMProviderConfig(
            id="",  # Empty string should fail regex pattern
            provider="vertex_ai",
            model_name="gemini-pro",
            tpm_limit=1000,
            rpm_limit=100,
        )


def test_llm_provider_config_temperature_bounds() -> None:
    """Test temperature validator triggers AppException on out-of-bounds values."""
    with pytest.raises(AppException) as exc_info:
        LLMProviderConfig(
            id="prv_vertexai123",
            provider="vertex_ai",
            model_name="gemini-pro",
            temperature=2.5,
            tpm_limit=1000,
            rpm_limit=100,
        )
    assert exc_info.value.status_code == 400
    assert "Temperature must be between 0.0 and 2.0" in exc_info.value.message


def test_llm_provider_config_top_p_bounds() -> None:
    """Test top_p validator triggers AppException on out-of-bounds values."""
    with pytest.raises(AppException) as exc_info:
        LLMProviderConfig(
            id="prv_vertexai123",
            provider="vertex_ai",
            model_name="gemini-pro",
            top_p=1.5,
            tpm_limit=1000,
            rpm_limit=100,
        )
    assert exc_info.value.status_code == 400
    assert "top_p must be between 0.0 and 1.0" in exc_info.value.message


def test_llm_provider_config_penalties_bounds() -> None:
    """Test frequency_penalty and presence_penalty validators trigger AppException."""
    with pytest.raises(AppException) as exc_info_freq:
        LLMProviderConfig(
            id="prv_vertexai123",
            provider="vertex_ai",
            model_name="gemini-pro",
            frequency_penalty=3.0,
            tpm_limit=1000,
            rpm_limit=100,
        )
    assert exc_info_freq.value.status_code == 400

    with pytest.raises(AppException) as exc_info_pres:
        LLMProviderConfig(
            id="prv_vertexai123",
            provider="vertex_ai",
            model_name="gemini-pro",
            presence_penalty=-3.0,
            tpm_limit=1000,
            rpm_limit=100,
        )
    assert exc_info_pres.value.status_code == 400


def test_llm_response_valid() -> None:
    """Test valid instantiation of LLMResponse."""
    response = LLMResponse(
        content="Success",
        token_usage=TokenUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10),
        provider_metadata=ProviderMetadataDTO(finish_reason="stop"),
        messages=[LLMMessageDTO(role="user", content="Hello")],
    )
    assert response.content == "Success"
    assert response.provider_metadata.finish_reason == "stop"
    assert len(response.messages or []) == 1


@pytest.mark.parametrize("empty_val", ["null", "None", "N/A", "ei saatavilla", "  NULL  "])
def test_llm_response_invalid_empty_strings(empty_val: str) -> None:
    """Test validate_non_empty triggers AppException on placeholder strings."""
    with pytest.raises(AppException) as exc_info:
        LLMResponse(
            content=empty_val,
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10),
        )
    assert exc_info.value.status_code == 400
    assert "LLM returned an invalid empty-equivalent string" in exc_info.value.message


def test_adhoc_test_models() -> None:
    """Test AdHocTestRequest and AdHocTestResponse instantiation and validation."""
    req = AdHocTestRequest(
        provider="openai",
        system_instruction="System",
        user_prompt="User",
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    assert req.provider == "openai"

    resp = AdHocTestResponse(
        content="Response text",
        latency_ms=120.5,
        status="success",
    )
    assert resp.status == "success"
    assert resp.latency_ms == 120.5
