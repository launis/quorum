from enum import Enum
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import LLMSchemaValidationError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.llm import LLMProviderConfig


class MockEvidenceType(str, Enum):
    EXPLICIT_QUOTE = "EXPLICIT_QUOTE"
    NO_EVIDENCE = "NO_EVIDENCE"


class MockStrictResponseSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    evidence: MockEvidenceType


class MockResponseSchema(BaseModel):
    value: str


@pytest.fixture
def mock_config() -> LLMProviderConfig:
    return LLMProviderConfig(
        id="litellm/fast",
        provider="litellm",
        model_name="gpt-4o-mini",
        temperature=0.0,
        default_max_tokens=1000,
        tpm_limit=100000,
        rpm_limit=1000,
    )


@pytest.fixture
def mock_provider() -> AsyncMock:
    provider = AsyncMock()
    return provider


@pytest.mark.asyncio
async def test_client_run_structured_task_success(mock_config: LLMProviderConfig, mock_provider: AsyncMock) -> None:
    client = LLMClient(config=mock_config)

    mock_response = AsyncMock()
    mock_response.content = '{"value": "hello"}'
    mock_response.token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 15,
        "total_tokens": 25,
        "cached_tokens": 0,
        "reasoning_tokens": 0,
        "cost_usd": 0.0,
    }
    mock_provider.generate.return_value = mock_response

    with patch("backend_v2.llm.client.LLMFactory.create_provider", return_value=mock_provider):
        validated_model, usage = await client.run_structured_task(
            messages=[{"role": "user", "content": "hi"}], response_model=MockResponseSchema
        )

        assert validated_model.value == "hello"
        assert isinstance(usage, TokenUsage)
        assert usage.total_tokens == 25
        mock_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_client_run_structured_task_json_error(mock_config: LLMProviderConfig, mock_provider: AsyncMock) -> None:
    client = LLMClient(config=mock_config)

    mock_response = AsyncMock()
    mock_response.content = "not valid json"
    mock_response.token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 15,
        "total_tokens": 25,
        "cached_tokens": 0,
        "reasoning_tokens": 0,
        "cost_usd": 0.0,
    }
    mock_provider.generate.return_value = mock_response

    with patch("backend_v2.llm.client.LLMFactory.create_provider", return_value=mock_provider):
        with pytest.raises(LLMSchemaValidationError) as exc_info:
            await client.run_structured_task(
                messages=[{"role": "user", "content": "hi"}], response_model=MockResponseSchema
            )

        assert exc_info.value.raw_llm_payload == "not valid json"
        assert exc_info.value.is_eof is False


@pytest.mark.asyncio
async def test_client_run_chat(mock_config: LLMProviderConfig, mock_provider: AsyncMock) -> None:
    client = LLMClient(config=mock_config)

    mock_response = AsyncMock()
    mock_response.content = "chat response"
    mock_response.tool_calls = None
    mock_provider.generate.return_value = mock_response

    with patch("backend_v2.llm.client.LLMFactory.create_provider", return_value=mock_provider):
        result = await client.run_chat(messages=[{"role": "user", "content": "hi"}])
        assert result == "chat response"
        mock_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_client_run_structured_task_strict_enum(mock_config: LLMProviderConfig, mock_provider: AsyncMock) -> None:
    client = LLMClient(config=mock_config)

    mock_response = AsyncMock()
    mock_response.content = '{"evidence": "EXPLICIT_QUOTE"}'
    mock_response.token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 15,
        "total_tokens": 25,
        "cached_tokens": 0,
        "reasoning_tokens": 0,
        "cost_usd": 0.0,
    }
    mock_provider.generate.return_value = mock_response

    with patch("backend_v2.llm.client.LLMFactory.create_provider", return_value=mock_provider):
        validated_model, usage = await client.run_structured_task(
            messages=[{"role": "user", "content": "hi"}], response_model=MockStrictResponseSchema
        )

        assert validated_model.evidence == MockEvidenceType.EXPLICIT_QUOTE
        assert usage.total_tokens == 25
