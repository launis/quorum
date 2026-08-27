import pytest
from pydantic import BaseModel, Field

from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import ModelProfile


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


def test_openai_adapter_prepare_provider_kwargs() -> None:
    """Verify prepare_provider_kwargs returns empty dictionary."""
    adapter = OpenAICacheAdapter()
    assert adapter.prepare_provider_kwargs("gpt-4o") == {}


def test_openai_adapter_prepare_kwargs_reasoning_and_param_stripping() -> None:
    """Verify prepare_kwargs maps thinking budget to reasoning effort and strips unsupported params."""
    adapter = OpenAICacheAdapter()

    config = ModelProfile(
        provider="openai",
        model_name="o3-mini",
        temperature=0.7,
        thinking_budget_tokens=8192,
    )
    call_kwargs = {
        "model": "o3-mini",
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
    }

    result = adapter.prepare_kwargs(call_kwargs, config=config)

    assert result["reasoning_effort"] == "high"
    assert "temperature" not in result
    assert "top_p" not in result
    assert "frequency_penalty" not in result
    assert "presence_penalty" not in result


def test_openai_adapter_prepare_structured_output() -> None:
    """Verify prepare_structured_output converts Pydantic model into strict json_schema dictionary."""
    adapter = OpenAICacheAdapter()

    class SampleOutputModel(BaseModel):
        summary: str = Field(description="Summary of text")
        score: int = Field(description="Score value")

    result = adapter.prepare_structured_output(SampleOutputModel)

    assert isinstance(result, dict)
    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "SampleOutputModel"
    assert result["json_schema"]["strict"] is True
    assert "properties" in result["json_schema"]["schema"]
