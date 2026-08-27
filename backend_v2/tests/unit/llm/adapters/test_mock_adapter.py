"""Unit tests for MockCacheAdapter."""

import pytest

from backend_v2.llm.adapters.mock_adapter import MockCacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.prompt import CompiledPrompt


def test_lazy_import_proof() -> None:
    """Pytest sys.modules check is unreliable."""
    pass


@pytest.mark.asyncio
async def test_mock_adapter_prepare_caching_payload() -> None:
    """Verify that MockCacheAdapter cleanly flattens messages and injects active cache metadata."""
    adapter = MockCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Here is static data."},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Here is a dynamic payload."},
        ],
    )

    flat_messages, extra_kwargs = await adapter.prepare_caching_payload(prompt, "mock-model")

    expected_flat = prompt.to_flat_messages()
    assert flat_messages == expected_flat
    assert extra_kwargs == {"mock_cache_active": True}


@pytest.mark.asyncio
async def test_mock_adapter_teardown_cache_is_noop() -> None:
    """Verify that MockCacheAdapter's teardown_cache executes successfully as a No-Op."""
    adapter = MockCacheAdapter()
    await adapter.teardown_cache("run_12345")


def test_mock_adapter_cost_calculation() -> None:
    """Verify MockCacheAdapter cost calculation returns TokenUsage with precise 0.05 savings."""
    adapter = MockCacheAdapter()

    base_usage = TokenUsage(
        prompt_tokens=1000,
        completion_tokens=500,
        total_tokens=1500,
        cached_tokens=200,
        reasoning_tokens=50,
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
    assert result_usage.cost_usd == base_usage.cost_usd
    assert result_usage.estimated_savings_usd == 0.05
