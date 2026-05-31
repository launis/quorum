"""Unit and precision cost-calculation tests for DeepSeekCacheAdapter."""

import sys
from typing import cast

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.deepseek_adapter import DeepSeekCacheAdapter
from backend_v2.llm.adapters.openai_adapter import OpenAITokenUsage
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


def test_lazy_import_proof() -> None:
    """Verify that importing DeepSeekCacheAdapter does not globally load heavy ML libraries."""
    heavy_libs = ["vertexai", "anthropic", "openai", "litellm", "google.genai"]
    for lib in heavy_libs:
        assert lib not in sys.modules, f"Heavy ML library '{lib}' was unexpectedly loaded globally!"


@pytest.mark.asyncio
async def test_deepseek_adapter_preparer() -> None:
    """Verify DeepSeek adapter prepares flat messages with empty extra_kwargs."""
    deepseek_adapter = DeepSeekCacheAdapter()
    
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "User static content."},
        ],
        dynamic_messages=[
            {"role": "assistant", "content": "Response."},
        ],
    )
    
    ds_messages, ds_kwargs = await deepseek_adapter.prepare_caching_payload(prompt, "deepseek-chat")
    assert ds_messages == prompt.to_flat_messages()
    assert ds_kwargs == {}


@pytest.mark.asyncio
async def test_deepseek_teardown_is_noop() -> None:
    """Verify teardown is successfully executed as No-Op."""
    adapter = DeepSeekCacheAdapter()
    await adapter.teardown_cache("run_12345")


def test_deepseek_precision_calculation_scenarios() -> None:
    """Test mathematical precision and ROI scenarios for DeepSeekCacheAdapter."""
    deepseek_adapter = DeepSeekCacheAdapter()
    
    pricing = {"input_token_price": 0.000005, "output_token_price": 0.000015}
    
    # Scenario 1: DeepSeek with cached tokens (90% read discount)
    usage_cached = TokenUsage(prompt_tokens=1000, completion_tokens=500, cached_tokens=600)
    result_ds = cast(OpenAITokenUsage, deepseek_adapter.calculate_cost(usage_cached, pricing))
    assert isinstance(result_ds, OpenAITokenUsage)
    # regular = 1000 - 600 = 400
    # Cost = 400 * 0.000005 + 600 * 0.000005 * 0.10 + 500 * 0.000015
    #      = 0.002 + 0.0003 + 0.0075 = 0.0098
    # Savings = 600 * 0.000005 * 0.90 = 0.0027
    assert result_ds.cost_usd == pytest.approx(0.0098)
    assert result_ds.estimated_savings_usd == pytest.approx(0.0027)


def test_missing_pricing_raises_error() -> None:
    """Verify that DeepSeek adapter raises AppException when price configuration is missing."""
    deepseek = DeepSeekCacheAdapter()
    usage = TokenUsage(prompt_tokens=100)
    
    with pytest.raises(AppException) as exc_info:
        deepseek.calculate_cost(usage, {})
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value
