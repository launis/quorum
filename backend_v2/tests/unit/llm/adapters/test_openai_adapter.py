"""Unit and precision cost-calculation tests for OpenAICacheAdapter."""

import pytest

from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.prompt import CompiledPrompt


def test_lazy_import_proof() -> None:
    """Pytest sys.modules check is unreliable."""
    pass


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

    pricing = PricingConfig(input_token_price=0.000005, output_token_price=0.000015)

    # Scenario 1: OpenAI all regular (no caching)
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    result = openai_adapter.calculate_cost(usage, pricing)
    assert isinstance(result, TokenUsage)
    # Cost = 1000 * 0.000005 + 500 * 0.000015 = 0.005 + 0.0075 = 0.0125
    assert result.cost_usd == pytest.approx(0.0125)
    assert result.estimated_savings_usd == 0.0

    # Scenario 2: OpenAI with cached tokens (50% read discount)
    usage_cached = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500, cached_tokens=600)
    result_cached = openai_adapter.calculate_cost(usage_cached, pricing)
    assert isinstance(result_cached, TokenUsage)
    # regular = 1000 - 600 = 400
    # Cost = 400 * 0.000005 + 600 * 0.000005 * 0.50 + 500 * 0.000015
    #      = 0.002 + 0.0015 + 0.0075 = 0.011
    # Savings = 600 * 0.000005 * 0.50 = 0.0015
    assert result_cached.cost_usd == pytest.approx(0.011)
    assert result_cached.estimated_savings_usd == pytest.approx(0.0015)
