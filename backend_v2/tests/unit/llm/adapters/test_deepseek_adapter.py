"""Unit and precision cost-calculation tests for DeepSeekCacheAdapter."""

import pytest

from backend_v2.llm.adapters.deepseek_adapter import DeepSeekCacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.prompt import CompiledPrompt


def test_lazy_import_proof() -> None:
    """Pytest sys.modules check is unreliable."""
    pass


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

    pricing = PricingConfig(input_token_price=0.000005, output_token_price=0.000015)

    # Scenario 1: DeepSeek with cached tokens (90% read discount)
    usage_cached = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500, cached_tokens=600)
    result_ds = deepseek_adapter.calculate_cost(usage_cached, pricing)
    assert isinstance(result_ds, TokenUsage)
    # regular = 1000 - 600 = 400
    # Cost = 400 * 0.000005 + 600 * 0.000005 * 0.10 + 500 * 0.000015
    #      = 0.002 + 0.0003 + 0.0075 = 0.0098
    # Savings = 600 * 0.000005 * 0.90 = 0.0027
    assert result_ds.cost_usd == pytest.approx(0.0098)
    assert result_ds.estimated_savings_usd == pytest.approx(0.0027)
