from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.llm.client import LLMClient


class DummyConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    provider: str = "lite_llm"
    model_name: str = "pytest-model-1"
    temperature: float = 0.0
    default_max_tokens: int = 1000
    is_active: bool = True
    tpm_limit: int = 10000
    rpm_limit: int = 1000
    caching_strategy: str = "none"
    top_p: float | None = None
    top_k: int | None = None


class JSONRepairTestSchema(BaseModel):
    exact_quote: str | None = Field(default=None)
    step_4_final_score: int


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_json_repair_trailing_quotes(mock_create_provider: MagicMock) -> None:
    """Reproduce the production crash where LLM returns unescaped double quotes.

    It returns trailing double quotes at the end of a non-empty string value:
    ryhmätyötiloiksi."",
    This fails validation because of invalid JSON syntax.
    """
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cost_usd": 0.01,
    }

    # The exact malformed JSON layout from the production crash
    malformed_payload = (
        "{\n"
        '  "exact_quote": "1. Talous ja tilatehokkuus\\nSiirrytään yhteiskäyttöisiin '
        "tiimitiloihin ja hiljaisen työn huoneisiin. Tämä säästää kiinteistökuluja "
        'ja vapauttaa neliöitä opiskelijoiden ryhmätyötiloiksi."",\n'
        '  "step_4_final_score": 5\n'
        "}"
    )

    mock_response = MagicMock()
    mock_response.content = malformed_payload
    mock_response.token_usage = usage
    mock_provider.generate.return_value = mock_response

    client = LLMClient(config=cast(Any, DummyConfig()))

    # Run the task. Since the raw payload is malformed, this should throw
    # LLMSchemaValidationError (or AgentExecutionError if retries are depleted).
    # We expect this test to FAIL (raising the error) before the fix is applied.
    # After the fix, it should PASS.
    res, total_usage = await client.run_structured_task(
        messages=[{"role": "user", "content": "Test"}], response_model=JSONRepairTestSchema
    )

    assert res.step_4_final_score == 5
    assert res.exact_quote is not None
    assert res.exact_quote.endswith('ryhmätyötiloiksi."')


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_json_repair_other_best_practices(mock_create_provider: MagicMock) -> None:
    """Verify other JSON repair best practices (trailing commas, control chars in strings)."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "cost_usd": 0.01}

    # Payload with raw newlines/tabs inside exact_quote, and a trailing comma in step_4_final_score
    malformed_payload = '{\n  "exact_quote": "line1\nline2\twith\ttabs",\n  "step_4_final_score": 5,\n}'

    mock_response = MagicMock()
    mock_response.content = malformed_payload
    mock_response.token_usage = usage
    mock_provider.generate.return_value = mock_response

    client = LLMClient(config=cast(Any, DummyConfig()))

    res, total_usage = await client.run_structured_task(
        messages=[{"role": "user", "content": "Test"}], response_model=JSONRepairTestSchema
    )

    assert res.step_4_final_score == 5
    assert res.exact_quote == "line1\nline2\twith\ttabs"
