from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import LLMSchemaValidationError
from backend_v2.llm.client import LLMClient


class DummyConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "llm_abc123456"
    provider: str = "openai"
    model_name: str = "pytest-model-1"
    temperature: float = 0.0
    default_max_tokens: int = 1000
    is_active: bool = True
    tpm_limit: int = 10000
    rpm_limit: int = 1000
    caching_strategy: str = "none"
    top_p: float | None = None
    top_k: int | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None


class DummyModel(BaseModel):
    field1: str


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_empty_content_raises_schema_error_for_healing(mock_create_provider: MagicMock) -> None:
    """Tier 3: Ensure empty LLM responses trigger LLMSchemaValidationError for self-healing."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    # Simulate Gemini 2.5 "Thinking Loop" katatonia / empty response
    mock_response = MagicMock()
    mock_response.content = None
    mock_response.token_usage = {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10}

    mock_provider.generate.return_value = mock_response

    client = LLMClient(config=DummyConfig().model_dump())

    with pytest.raises(LLMSchemaValidationError) as exc:
        await client.run_structured_task(messages=[{"role": "user", "content": "hello"}], response_model=DummyModel)

    assert exc.value.is_eof is True
    assert "Safety Filter Triggered" in exc.value.validation_error_msg
