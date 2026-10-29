"""Unit and precision cost-calculation tests for DeepSeekCacheAdapter."""

from __future__ import annotations

from typing import Annotated, Any

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.deepseek_adapter import DeepSeekCacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt


@pytest.mark.asyncio
async def test_deepseek_adapter_preparer() -> None:
    """Verify DeepSeek adapter prepares flat messages with empty extra_kwargs."""
    deepseek_adapter = DeepSeekCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content="You are a helpful assistant."),
            LLMMessageDTO(role="user", content="User static content."),
        ],
        dynamic_messages=[
            LLMMessageDTO(role="assistant", content="Response."),
        ],
    )

    res = await deepseek_adapter.prepare_caching_payload(prompt, "deepseek-chat")
    assert res.messages == prompt.to_flat_messages()
    assert res.kwargs == {}


@pytest.mark.asyncio
async def test_deepseek_teardown_is_noop() -> None:
    """Verify teardown is successfully executed as No-Op."""
    adapter = DeepSeekCacheAdapter()
    await adapter.teardown_cache("run_12345")


def test_deepseek_prepare_provider_kwargs() -> None:
    """Verify prepare_provider_kwargs returns an empty dictionary for valid model names."""
    adapter = DeepSeekCacheAdapter()
    assert adapter.prepare_provider_kwargs("deepseek/deepseek-chat") == {}


def test_deepseek_prepare_provider_kwargs_empty_model_raises_app_exception() -> None:
    """Negative test: Verify prepare_provider_kwargs raises AppException on empty or whitespace model_name."""
    adapter = DeepSeekCacheAdapter()

    with pytest.raises(AppException) as exc_info:
        adapter.prepare_provider_kwargs("   ")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_deepseek_prepare_structured_output() -> None:
    """Verify prepare_structured_output builds strict JSON schema and strips unsupported constraints."""
    adapter = DeepSeekCacheAdapter()

    class DeepSeekSampleModel(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")

        summary: Annotated[str, Field(min_length=3, max_length=100, description="Summary text.")]
        score: Annotated[int, Field(ge=1, le=5, description="Score rating.")]

    result = adapter.prepare_structured_output(DeepSeekSampleModel)
    assert type(result) is dict
    assert result["type"] == "json_schema"
    json_schema_block = result["json_schema"]
    assert json_schema_block["name"] == "DeepSeekSampleModel"
    assert json_schema_block["strict"] is True

    schema_props = json_schema_block["schema"]["properties"]
    assert "minLength" not in schema_props["summary"]
    assert "maxLength" not in schema_props["summary"]
    assert "minimum" not in schema_props["score"]
    assert "maximum" not in schema_props["score"]


def test_deepseek_prepare_structured_output_invalid_type_raises_app_exception() -> None:
    """Negative test: Verify prepare_structured_output raises AppException when given a non-BaseModel type."""
    adapter = DeepSeekCacheAdapter()
    invalid_model: Any = dict

    with pytest.raises(AppException) as exc_info:
        adapter.prepare_structured_output(invalid_model)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_deepseek_precision_calculation_scenarios() -> None:
    """Test mathematical precision, boundary values, and ROI scenarios for DeepSeekCacheAdapter."""
    deepseek_adapter = DeepSeekCacheAdapter()

    pricing = PricingConfig(input_token_price=0.000005, output_token_price=0.000015)

    # Scenario 1: DeepSeek with cached tokens (90% default read discount)
    usage_cached = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500, cached_tokens=600)
    result_ds = deepseek_adapter.calculate_cost(usage_cached, pricing)
    assert isinstance(result_ds, TokenUsage)
    # regular = 1000 - 600 = 400
    # Cost = 400 * 0.000005 + 600 * 0.000005 * 0.10 + 500 * 0.000015
    #      = 0.002 + 0.0003 + 0.0075 = 0.0098
    # Savings = 600 * 0.000005 * 0.90 = 0.0027
    assert result_ds.cost_usd == pytest.approx(0.0098)
    assert result_ds.estimated_savings_usd == pytest.approx(0.0027)

    # Scenario 2: Boundary value - Zero cached tokens (no cache hit)
    usage_no_cache = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500, cached_tokens=0)
    result_no_cache = deepseek_adapter.calculate_cost(usage_no_cache, pricing)
    assert result_no_cache.cost_usd == pytest.approx(0.0125)
    assert result_no_cache.estimated_savings_usd == 0.0

    # Scenario 3: Boundary value - cached_tokens exceeding prompt_tokens clamps regular_input to 0
    usage_clamped = TokenUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        cached_tokens=150,
        reasoning_tokens=20,
    )
    result_clamped = deepseek_adapter.calculate_cost(usage_clamped, pricing)
    # regular_input = max(0, 100 - 150) = 0
    # cost_cached = 150 * 0.000005 * 0.10 = 0.000075
    # cost_output = 50 * 0.000015 = 0.00075
    assert result_clamped.cost_usd == pytest.approx(0.000825)
    assert result_clamped.estimated_savings_usd == pytest.approx(150 * 0.000005 * 0.90)
    assert result_clamped.reasoning_tokens == 20

    # Scenario 4: Explicit cached_input_token_price from LiteLLM registry PricingConfig SSOT
    explicit_pricing = PricingConfig(
        input_token_price=0.000005,
        output_token_price=0.000015,
        cached_input_token_price=0.000001,
    )
    result_explicit = deepseek_adapter.calculate_cost(usage_cached, explicit_pricing)
    # regular = 400 * 0.000005 = 0.002
    # cached = 600 * 0.000001 = 0.0006
    # output = 500 * 0.000015 = 0.0075 -> total = 0.0101
    # savings = 600 * (0.000005 - 0.000001) = 0.0024
    assert result_explicit.cost_usd == pytest.approx(0.0101)
    assert result_explicit.estimated_savings_usd == pytest.approx(0.0024)


def test_deepseek_negative_boundary_schema_validation() -> None:
    """Negative boundary test: Verify negative token counts or negative prices fail fast at DTO boundary."""
    with pytest.raises(ValidationError):
        PricingConfig(input_token_price=-0.0001, output_token_price=0.000015)

    with pytest.raises(ValidationError):
        TokenUsage(prompt_tokens=-1, completion_tokens=10, total_tokens=9)
