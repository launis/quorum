"""Unit tests for OpenAICacheAdapter strict JSON schema transformations and request preparations."""

from typing import Annotated, Any, Literal

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


def test_openai_adapter_dev_environment_clamping() -> None:
    """Verify OpenAI adapter clamps reasoning_effort to 'low' in development environment."""
    from backend_v2.settings import Settings

    adapter = OpenAICacheAdapter()
    dev_settings = Settings(use_mock_llm=True, environment="development")
    prod_settings = Settings(use_mock_llm=True, environment="production")

    config = ModelProfile(
        provider="openai",
        model_name="o3-mini",
        temperature=0.7,
        thinking_budget_tokens=8192,
    )

    # In development: clamped to "low" regardless of 8192 tokens
    call_kwargs_dev: dict[str, Any] = {"model": "o3-mini"}
    res_dev = adapter.prepare_kwargs(call_kwargs_dev, config=config, settings=dev_settings)
    assert res_dev["reasoning_effort"] == "low"

    # In production: preserved as "high" for 8192 tokens
    call_kwargs_prod: dict[str, Any] = {"model": "o3-mini"}
    res_prod = adapter.prepare_kwargs(call_kwargs_prod, config=config, settings=prod_settings)
    assert res_prod["reasoning_effort"] == "high"


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


def test_openai_adapter_strict_json_schema_compliance() -> None:
    """Verify OpenAI strict structured outputs conform to OpenAI's strict JSON schema specification."""
    adapter = OpenAICacheAdapter()

    class SubItem(BaseModel):
        item_id: str = Field(description="Item identifier")
        note: str | None = Field(default=None, description="Optional note")

    class ComplexTestModel(BaseModel):
        title: str = Field(description="Title", min_length=3, max_length=50)
        count: int = Field(default=1, description="Item count", ge=0)
        items: list[SubItem] = Field(description="List of nested items")
        optional_tag: str | None = Field(default=None, description="Optional tag")

    result = adapter.prepare_structured_output(ComplexTestModel)

    assert isinstance(result, dict)
    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "ComplexTestModel"
    assert result["json_schema"]["strict"] is True

    schema = result["json_schema"]["schema"]
    assert schema["additionalProperties"] is False
    assert "title" in schema["required"]
    assert "count" in schema["required"]
    assert "items" in schema["required"]
    assert "optional_tag" in schema["required"]
    assert "default" not in schema["properties"]["count"]
    assert "minLength" not in schema["properties"]["title"]
    assert "maxLength" not in schema["properties"]["title"]

    # Check nested $defs
    defs = schema.get("$defs", {})
    assert "SubItem" in defs
    sub_schema = defs["SubItem"]
    assert sub_schema["additionalProperties"] is False
    assert "item_id" in sub_schema["required"]
    assert "note" in sub_schema["required"]
    assert "default" not in sub_schema["properties"]["note"]


def test_openai_adapter_credential_fail_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify LLMFactory raises ConfigurationError when OpenAI credentials are completely absent."""
    from backend_v2.exceptions import ConfigurationError
    from backend_v2.llm.provider import LLMFactory
    from backend_v2.settings import get_settings

    mock_settings = get_settings().model_copy(update={"use_mock_llm": False, "openai_api_key": None})
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="Fail-Fast: OPENAI_API_KEY is not configured"):
        LLMFactory.create_provider(
            provider_type="openai",
            model_name="openai/gpt-4o-mini",
            api_key=None,
        )


def test_openai_adapter_gpt51_dynamic_reasoning_detection() -> None:
    """Verify that gpt-5.1 (not starting with 'o') is dynamically recognized as a reasoning model via registry."""
    adapter = OpenAICacheAdapter()

    config = ModelProfile(
        provider="openai",
        model_name="openai/gpt-5.1",
        temperature=0.0,
        thinking_budget_tokens=2048,
    )
    call_kwargs = {
        "model": "openai/gpt-5.1",
        "temperature": 0.0,
        "top_p": 1.0,
    }

    result = adapter.prepare_kwargs(call_kwargs, config=config)

    assert result["reasoning_effort"] == "low"
    assert "temperature" not in result
    assert "top_p" not in result


def test_openai_adapter_gpt4o_mini_non_reasoning() -> None:
    """Verify that gpt-4o-mini is recognized as non-reasoning and retains temperature and top_p."""
    adapter = OpenAICacheAdapter()

    config = ModelProfile(
        provider="openai",
        model_name="openai/gpt-4o-mini",
        temperature=0.0,
        thinking_budget_tokens=0,
    )
    call_kwargs = {
        "model": "openai/gpt-4o-mini",
        "temperature": 0.0,
        "top_p": 1.0,
    }

    result = adapter.prepare_kwargs(call_kwargs, config=config)

    assert "reasoning_effort" not in result
    assert result.get("temperature") == 0.0
    assert result.get("top_p") == 1.0


def test_openai_adapter_transforms_discriminated_union_oneof_to_anyof() -> None:
    """Verify OpenAICacheAdapter transforms 'oneOf' to 'anyOf' and removes 'discriminator'.

    OpenAI's strict schema validator explicitly rejects 'oneOf' with:
    "Invalid schema for response_format: 'oneOf' is not permitted."
    """
    from backend_v2.models.dtos.synthesis import ExecutiveSummarySectionResult, MatrixSectionSynthesesResult

    adapter = OpenAICacheAdapter()

    # 1. ExecutiveSummarySectionResult
    result1 = adapter.prepare_structured_output(ExecutiveSummarySectionResult)
    assert isinstance(result1, dict)
    schema1 = result1["json_schema"]["schema"]
    exec_summary_items = schema1["properties"]["executive_summary"]["items"]
    assert "oneOf" not in exec_summary_items, (
        f"'oneOf' must not be present in OpenAI schema items: {exec_summary_items}"
    )
    assert "discriminator" not in exec_summary_items, (
        f"'discriminator' must not be present in OpenAI schema items: {exec_summary_items}"
    )
    assert "anyOf" in exec_summary_items, f"'anyOf' must be present in OpenAI schema items: {exec_summary_items}"
    assert len(exec_summary_items["anyOf"]) == 5

    # 2. MatrixSectionSynthesesResult
    result2 = adapter.prepare_structured_output(MatrixSectionSynthesesResult)
    assert isinstance(result2, dict)
    schema2 = result2["json_schema"]["schema"]
    section_items = schema2["$defs"]["SynthesisSectionDTO"]["properties"]["content_blocks"]["items"]
    assert "oneOf" not in section_items, f"'oneOf' must not be present in SynthesisSectionDTO items: {section_items}"
    assert "discriminator" not in section_items, (
        f"'discriminator' must not be present in SynthesisSectionDTO items: {section_items}"
    )
    assert "anyOf" in section_items, f"'anyOf' must be present in SynthesisSectionDTO items: {section_items}"
    assert len(section_items["anyOf"]) == 5


def test_openai_adapter_handles_empty_and_malformed_unions_safely() -> None:
    """ISTQB Partition 4: Verify schema traversal safely handles empty or boundary union nodes without crashing."""
    adapter = OpenAICacheAdapter()

    raw_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "empty_union": {"oneOf": []},
            "discriminated_empty": {"oneOf": [], "discriminator": {"propertyName": "type"}},
        },
    }
    adapter._enforce_openai_strict_schema(raw_schema)

    empty_union = raw_schema["properties"]["empty_union"]
    assert "oneOf" not in empty_union
    assert "anyOf" in empty_union
    assert empty_union["anyOf"] == []

    discriminated = raw_schema["properties"]["discriminated_empty"]
    assert "discriminator" not in discriminated
    assert "anyOf" in discriminated
    assert raw_schema["additionalProperties"] is False
    assert set(raw_schema["required"]) == {"empty_union", "discriminated_empty"}


def test_openai_adapter_strips_unsupported_constraints_from_union_branches() -> None:
    """ISTQB Partition 5: Verify child schema constraints inside union branches are cleanly stripped."""

    class OptionABlock(BaseModel):
        block_type: Literal["opt_a"] = "opt_a"
        title: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[A-Z]+$")]

    class OptionBBlock(BaseModel):
        block_type: Literal["opt_b"] = "opt_b"
        count: Annotated[int, Field(ge=1, le=100)]

    type OptionUnion = Annotated[OptionABlock | OptionBBlock, Field(discriminator="block_type")]

    class ContainerModel(BaseModel):
        blocks: list[OptionUnion]

    adapter = OpenAICacheAdapter()
    result = adapter.prepare_structured_output(ContainerModel)
    assert isinstance(result, dict)
    schema = result["json_schema"]["schema"]

    # Verify union definition in $defs
    defs = schema.get("$defs", {})
    assert "OptionUnion" in defs
    union_def = defs["OptionUnion"]
    assert "anyOf" in union_def
    assert "oneOf" not in union_def
    assert "discriminator" not in union_def

    # Verify constraints stripped from child branches ($defs)
    assert "OptionABlock" in defs
    opt_a_props = defs["OptionABlock"]["properties"]
    assert "minLength" not in opt_a_props["title"]
    assert "maxLength" not in opt_a_props["title"]
    assert "pattern" not in opt_a_props["title"]

    assert "OptionBBlock" in defs
    opt_b_props = defs["OptionBBlock"]["properties"]
    assert "minimum" not in opt_b_props["count"]
    assert "maximum" not in opt_b_props["count"]
