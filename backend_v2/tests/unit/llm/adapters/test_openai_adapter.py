"""Unit and precision cost-calculation tests for OpenAICacheAdapter."""

import sys
from typing import cast

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter, OpenAITokenUsage
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


def test_lazy_import_proof() -> None:
    """Verify that importing OpenAICacheAdapter does not globally load heavy ML libraries."""
    heavy_libs = ["vertexai", "anthropic", "openai", "litellm", "google.genai"]
    for lib in heavy_libs:
        assert lib not in sys.modules, f"Heavy ML library '{lib}' was unexpectedly loaded globally!"


@pytest.mark.asyncio
async def test_openai_adapter_preparer() -> None:
    """Verify OpenAI adapter prepares flat messages with empty extra_kwargs."""
    openai_adapter = OpenAICacheAdapter()
    
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "User static content."},
        ],
        dynamic_messages=[
            {"role": "assistant", "content": "Response."},
        ],
    )
    
    op_messages, op_kwargs = await openai_adapter.prepare_caching_payload(prompt, "gpt-4o")
    assert op_messages == prompt.to_flat_messages()
    assert op_kwargs == {}


@pytest.mark.asyncio
async def test_openai_teardown_is_noop() -> None:
    """Verify teardown is successfully executed as No-Op."""
    adapter = OpenAICacheAdapter()
    await adapter.teardown_cache("run_12345")


def test_openai_precision_calculation_scenarios() -> None:
    """Test mathematical precision and ROI scenarios for OpenAICacheAdapter."""
    openai_adapter = OpenAICacheAdapter()
    
    pricing = {"input_token_price": 0.000005, "output_token_price": 0.000015}
    
    # Scenario 1: OpenAI all regular (no caching)
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=500)
    result = cast(OpenAITokenUsage, openai_adapter.calculate_cost(usage, pricing))
    assert isinstance(result, OpenAITokenUsage)
    # Cost = 1000 * 0.000005 + 500 * 0.000015 = 0.005 + 0.0075 = 0.0125
    assert result.cost_usd == pytest.approx(0.0125)
    assert result.estimated_savings_usd == 0.0
    
    # Scenario 2: OpenAI with cached tokens (50% read discount)
    usage_cached = TokenUsage(prompt_tokens=1000, completion_tokens=500, cached_tokens=600)
    result = cast(OpenAITokenUsage, openai_adapter.calculate_cost(usage_cached, pricing))
    # regular = 1000 - 600 = 400
    # Cost = 400 * 0.000005 + 600 * 0.000005 * 0.50 + 500 * 0.000015
    #      = 0.002 + 0.0015 + 0.0075 = 0.011
    # Savings = 600 * 0.000005 * 0.50 = 0.0015
    assert result.cost_usd == pytest.approx(0.011)
    assert result.estimated_savings_usd == pytest.approx(0.0015)
    
    # Scenario 3: OpenAI dynamic recognition based on model name in config
    pricing_ds_name = {
        "input_token_price": 0.000005,
        "output_token_price": 0.000015,
        "model_name": "deepseek-coder",
    }
    result_ds_dynamic = cast(OpenAITokenUsage, openai_adapter.calculate_cost(usage_cached, pricing_ds_name))
    # DeepSeek read discount is 90%
    # regular = 400
    # Cost = 400 * 0.000005 + 600 * 0.000005 * 0.10 + 500 * 0.000015 = 0.0098
    assert result_ds_dynamic.cost_usd == pytest.approx(0.0098)
    assert result_ds_dynamic.estimated_savings_usd == pytest.approx(0.0027)


def test_missing_pricing_raises_error() -> None:
    """Verify that OpenAI adapter raises AppException when price configuration is missing."""
    openai = OpenAICacheAdapter()
    usage = TokenUsage(prompt_tokens=100)
    
    with pytest.raises(AppException) as exc_info:
        openai.calculate_cost(usage, {"output_token_price": 0.0002})
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value
