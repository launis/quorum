"""Unit and negative boundary tests for MockCacheAdapter."""

from __future__ import annotations

from typing import Annotated, Any

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.mock_adapter import MockCacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt


@pytest.mark.asyncio
async def test_mock_adapter_prepare_caching_payload() -> None:
    """Verify that MockCacheAdapter cleanly flattens messages and injects active cache metadata."""
    adapter = MockCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content="You are a helpful assistant."),
            LLMMessageDTO(role="user", content="Here is static data."),
        ],
        dynamic_messages=[
            LLMMessageDTO(role="user", content="Here is a dynamic payload."),
        ],
    )

    res = await adapter.prepare_caching_payload(prompt, "mock-model")

    expected_flat = prompt.to_flat_messages()
    assert res.messages == expected_flat
    assert res.kwargs == {"mock_cache_active": True}


@pytest.mark.asyncio
async def test_mock_adapter_prepare_caching_payload_empty_model_raises_app_exception() -> None:
    """Negative test: Verify prepare_caching_payload raises AppException on empty or whitespace model_name."""
    adapter = MockCacheAdapter()
    prompt = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="System instruction.")],
        dynamic_messages=[LLMMessageDTO(role="user", content="Dynamic payload.")],
    )

    with pytest.raises(AppException) as exc_info:
        await adapter.prepare_caching_payload(prompt, "   ")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_mock_adapter_teardown_cache_is_noop() -> None:
    """Verify that MockCacheAdapter's teardown_cache executes successfully as a No-Op."""
    adapter = MockCacheAdapter()
    await adapter.teardown_cache("run_12345")


@pytest.mark.asyncio
async def test_mock_adapter_teardown_cache_empty_run_id_raises_app_exception() -> None:
    """Negative test: Verify teardown_cache raises AppException when workflow_run_id is empty or whitespace."""
    adapter = MockCacheAdapter()

    with pytest.raises(AppException) as exc_info:
        await adapter.teardown_cache("  ")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_mock_adapter_cost_calculation() -> None:
    """Verify MockCacheAdapter cost calculation returns TokenUsage with precise 0.05 savings."""
    adapter = MockCacheAdapter()

    base_usage = TokenUsage(
        prompt_tokens=1000,
        completion_tokens=500,
        total_tokens=1500,
        cached_tokens=200,
        reasoning_tokens=50,
        cache_creation_input_tokens=100,
        cost_usd=0.015,
    )

    pricing = PricingConfig(input_token_price=0.0, output_token_price=0.0)
    result_usage = adapter.calculate_cost(base_usage, pricing)

    assert isinstance(result_usage, TokenUsage)
    assert result_usage.prompt_tokens == base_usage.prompt_tokens
    assert result_usage.completion_tokens == base_usage.completion_tokens
    assert result_usage.total_tokens == base_usage.total_tokens
    assert result_usage.cached_tokens == base_usage.cached_tokens
    assert result_usage.reasoning_tokens == base_usage.reasoning_tokens
    assert result_usage.cache_creation_input_tokens == base_usage.cache_creation_input_tokens
    assert result_usage.cost_usd == base_usage.cost_usd
    assert result_usage.estimated_savings_usd == pytest.approx(0.05)


def test_mock_adapter_prepare_provider_kwargs() -> None:
    """Verify MockCacheAdapter returns empty dictionary for prepare_provider_kwargs."""
    adapter = MockCacheAdapter()
    assert adapter.prepare_provider_kwargs("mock-model") == {}


def test_mock_adapter_prepare_provider_kwargs_empty_model_raises_app_exception() -> None:
    """Negative test: Verify prepare_provider_kwargs raises AppException on empty or whitespace model_name."""
    adapter = MockCacheAdapter()

    with pytest.raises(AppException) as exc_info:
        adapter.prepare_provider_kwargs("")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_mock_adapter_prepare_structured_output() -> None:
    """Verify MockCacheAdapter prepares valid json_schema output structure and strips unsupported constraints."""

    class SampleMockModel(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")

        field_a: Annotated[str, Field(min_length=2, max_length=50, description="Sample field")]

    adapter = MockCacheAdapter()
    result = adapter.prepare_structured_output(SampleMockModel)
    assert type(result) is dict
    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "SampleMockModel"
    assert result["json_schema"]["strict"] is True
    schema_props = result["json_schema"]["schema"]["properties"]
    assert "minLength" not in schema_props["field_a"]
    assert "maxLength" not in schema_props["field_a"]


def test_mock_adapter_prepare_structured_output_invalid_type_raises_app_exception() -> None:
    """Negative test: Verify prepare_structured_output raises AppException when given a non-BaseModel type."""
    adapter = MockCacheAdapter()
    invalid_model: Any = dict

    with pytest.raises(AppException) as exc_info:
        adapter.prepare_structured_output(invalid_model)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_mock_adapter_negative_boundary_schema_validation() -> None:
    """Negative boundary test: Verify negative token counts or negative prices fail fast at DTO boundary."""
    with pytest.raises(ValidationError):
        PricingConfig(input_token_price=-0.01, output_token_price=0.0)

    with pytest.raises(ValidationError):
        TokenUsage(prompt_tokens=-1, completion_tokens=0, total_tokens=0)
