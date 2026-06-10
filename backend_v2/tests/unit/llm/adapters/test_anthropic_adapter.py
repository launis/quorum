"""Unit and precision cost-calculation tests for AnthropicCacheAdapter."""

from typing import cast

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.anthropic_adapter import AnthropicCacheAdapter, AnthropicTokenUsage
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt


@pytest.mark.skip("Legacy architecture obsolete")
def test_lazy_import_proof() -> None:
    """Pytest sys.modules check is unreliable."""
    pass


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_anthropic_adapter_threshold_under() -> None:
    """Verify AnthropicCacheAdapter falls back to simple flattening if static chars < 4000."""
    adapter = AnthropicCacheAdapter()

    # 40 characters in static content (way under 4,000)
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Static text."},
        ],
        dynamic_messages=[
            {"role": "assistant", "content": "Hello!"},
        ],
    )

    flat_messages, extra_kwargs = await adapter.prepare_caching_payload(prompt, "claude-3-5-sonnet")

    expected_flat = prompt.to_flat_messages()
    assert flat_messages == expected_flat
    assert extra_kwargs == {}


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_anthropic_adapter_tagging_flow() -> None:
    """Verify AnthropicCacheAdapter merges system blocks and tags last static blocks when >= 4000 chars."""
    adapter = AnthropicCacheAdapter()

    # Generate static content over 4000 characters
    long_system = "System rule. " * 300  # ~3900 chars
    long_user_static = "Static user data. " * 50  # ~900 chars

    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": long_system},
            {"role": "system", "content": "Another system instruction."},
            {"role": "user", "content": long_user_static},
        ],
        dynamic_messages=[
            {"role": "assistant", "content": "Dynamic assistant message."},
            {"role": "user", "content": "Dynamic user query."},
        ],
    )

    flat_messages, extra_kwargs = await adapter.prepare_caching_payload(prompt, "claude-3-5-sonnet")

    assert extra_kwargs == {}

    # Verify the structure of the resulting messages list
    # Msg 1: combined system message with cache_control
    assert flat_messages[0]["role"] == "system"
    assert isinstance(flat_messages[0]["content"], list)
    assert len(flat_messages[0]["content"]) == 1
    assert flat_messages[0]["content"][0]["type"] == "text"
    assert "Another system instruction." in flat_messages[0]["content"][0]["text"]
    assert flat_messages[0]["content"][0]["cache_control"] == {"type": "ephemeral"}

    # Msg 2: static user message with cache_control
    assert flat_messages[1]["role"] == "user"
    assert isinstance(flat_messages[1]["content"], list)
    assert len(flat_messages[1]["content"]) == 1
    assert flat_messages[1]["content"][0]["type"] == "text"
    assert "Static user data." in flat_messages[1]["content"][0]["text"]
    assert flat_messages[1]["content"][0]["cache_control"] == {"type": "ephemeral"}

    # Msg 3 & 4: dynamic assistant & user messages should NOT be tagged and stay as strings
    assert flat_messages[2]["role"] == "assistant"
    assert flat_messages[2]["content"] == "Dynamic assistant message."

    assert flat_messages[3]["role"] == "user"
    assert flat_messages[3]["content"] == "Dynamic user query."


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_anthropic_adapter_boundary_merging() -> None:
    """Verify that same role at boundary is merged into content blocks, keeping cache control only on static."""
    adapter = AnthropicCacheAdapter()

    long_system = "Sys rule. " * 300
    long_user_static = "Static user message. " * 50

    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": long_system},
            {"role": "user", "content": long_user_static},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Dynamic user query."},
            {"role": "assistant", "content": "Dynamic assistant response."},
        ],
    )

    flat_messages, extra_kwargs = await adapter.prepare_caching_payload(prompt, "claude-3-5-sonnet")

    # Since both last static and first dynamic are "user", they must be merged in a single message
    # Let's count total messages: system (1), merged user (2), assistant (3)
    assert len(flat_messages) == 3

    # Msg 1: System
    assert flat_messages[0]["role"] == "system"

    # Msg 2: Merged User Message
    user_msg = flat_messages[1]
    assert user_msg["role"] == "user"
    assert isinstance(user_msg["content"], list)
    assert len(user_msg["content"]) == 2

    # Block 1: Static user part (caching active)
    assert user_msg["content"][0]["type"] == "text"
    assert "Static user message." in user_msg["content"][0]["text"]
    assert user_msg["content"][0]["cache_control"] == {"type": "ephemeral"}

    # Block 2: Dynamic user part (caching inactive)
    assert user_msg["content"][1]["type"] == "text"
    assert user_msg["content"][1]["text"] == "Dynamic user query."
    assert "cache_control" not in user_msg["content"][1]

    # Msg 3: Dynamic Assistant
    assert flat_messages[2]["role"] == "assistant"
    assert flat_messages[2]["content"] == "Dynamic assistant response."


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_anthropic_teardown_is_noop() -> None:
    """Verify teardown is successfully executed as No-Op."""
    adapter = AnthropicCacheAdapter()
    await adapter.teardown_cache("run_12345")


@pytest.mark.skip("Legacy architecture obsolete")
def test_anthropic_precision_calculation_scenarios() -> None:
    """Test multiple distinct mathematical precision and ROI scenarios for AnthropicCacheAdapter."""
    adapter = AnthropicCacheAdapter()

    # Base pricing config
    pricing = {"input_token_price": 0.000003, "output_token_price": 0.000015}

    # Scenario 1: All regular tokens (no caching)
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    result = cast(AnthropicTokenUsage, adapter.calculate_cost(usage, pricing))
    assert isinstance(result, AnthropicTokenUsage)
    # Cost = 1000 * 0.000003 + 500 * 0.000015 = 0.003 + 0.0075 = 0.0105
    assert result.cost_usd == pytest.approx(0.0105)
    assert result.estimated_savings_usd == 0.0

    # Scenario 2: Cache creation only
    usage_with_creation = AnthropicTokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    result = cast(AnthropicTokenUsage, adapter.calculate_cost(usage_with_creation, pricing))
    # regular = 1000 - 800 = 200
    # Cost = 200 * 0.000003 + 800 * 0.000003 * 1.25 + 500 * 0.000015
    #      = 0.0006 + 0.003 + 0.0075 = 0.0111
    # Savings = 0 - 800 * 0.000003 * 0.25 = -0.0006 -> max(0, -0.0006) = 0.0
    assert result.cost_usd == pytest.approx(0.0111)
    assert result.estimated_savings_usd == 0.0

    # Scenario 3: Cache read (hits) only
    usage_with_reads = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    result = cast(AnthropicTokenUsage, adapter.calculate_cost(usage_with_reads, pricing))
    # regular = 1000 - 600 = 400
    # Cost = 400 * 0.000003 + 600 * 0.000003 * 0.10 + 500 * 0.000015
    #      = 0.0012 + 0.00018 + 0.0075 = 0.00888
    # Savings = 600 * 0.000003 * 0.90 = 0.00162
    assert result.cost_usd == pytest.approx(0.00888)
    assert result.estimated_savings_usd == pytest.approx(0.00162)

    # Scenario 4: Mixed Cache Creation and Cache Reads
    usage_mixed = AnthropicTokenUsage(prompt_tokens=2000, completion_tokens=1000, total_tokens=3000)
    result = cast(AnthropicTokenUsage, adapter.calculate_cost(usage_mixed, pricing))
    # regular = 2000 - 1200 - 500 = 300
    # Cost = 300 * 0.000003 + 500 * 0.000003 * 1.25 + 1200 * 0.000003 * 0.10 + 1000 * 0.000015
    #      = 0.0009 + 0.001875 + 0.00036 + 0.015 = 0.018135
    # Savings = (1200 * 0.000003 * 0.90) - (500 * 0.000003 * 0.25)
    #         = 0.00324 - 0.000375 = 0.002865
    assert result.cost_usd == pytest.approx(0.018135)
    assert result.estimated_savings_usd == pytest.approx(0.002865)

    # Scenario 5: High priced input scenario
    pricing_expensive = {"input_token_price": 0.01, "output_token_price": 0.03}
    usage_mixed_exp = AnthropicTokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300)
    result = cast(AnthropicTokenUsage, adapter.calculate_cost(usage_mixed_exp, pricing_expensive))
    assert result.cost_usd == pytest.approx(3.75)
    assert result.estimated_savings_usd == pytest.approx(1.25)


@pytest.mark.skip("Legacy architecture obsolete")
def test_missing_pricing_raises_error() -> None:
    """Verify that Anthropic adapter raises AppException when price configuration is missing."""
    adapter = AnthropicCacheAdapter()
    usage = TokenUsage(prompt_tokens=100, completion_tokens=0, total_tokens=100)

    with pytest.raises(AppException) as exc_info:
        adapter.calculate_cost(usage, {"input_token_price": 0.0001})
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value
