"""Unit tests for BaseLLMAdapter abstract class and rate pacing logic."""

from __future__ import annotations

from typing import Annotated, Any, Literal, override
from unittest.mock import AsyncMock, patch

import opentelemetry.trace as otel_trace
import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import (
    BaseLLMAdapter,
    apply_provider_pacing,
    get_redis_client_for_pacing,
)
from backend_v2.models.auth import ResolvedCredentialDTO
from backend_v2.models.domain.system_config import ModelProfile
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.enums import LLMProviderName
from backend_v2.models.llm import CachingPayloadResultDTO, LLMMessageDTO, LLMProviderConfig
from backend_v2.models.prompt import CompiledPrompt


class ConcreteAdapter(BaseLLMAdapter):
    """Concrete implementation for testing base adapter defaults."""

    @override
    async def prepare_caching_payload(
        self,
        compiled_prompt: CompiledPrompt,
        model_name: str,
        config: LLMProviderConfig | ModelProfile | None = None,
        resolved_credential: ResolvedCredentialDTO | None = None,
    ) -> CachingPayloadResultDTO:
        _ = (model_name, config, resolved_credential)
        return CachingPayloadResultDTO(messages=compiled_prompt.to_flat_messages(), kwargs={})

    @override
    async def teardown_cache(self, workflow_run_id: str) -> None:
        _ = workflow_run_id

    @override
    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        _ = pricing_config
        return usage

    @override
    def prepare_provider_kwargs(self, model_name: str) -> Any:
        _ = model_name
        return {}

    @override
    def prepare_structured_output(self, response_model: type[BaseModel]) -> Any:
        schema = response_model.model_json_schema()
        self._strip_unsupported_constraints(schema)
        return schema


def test_base_adapter_defaults() -> None:
    """Verify default implementations of non-abstract methods in BaseLLMAdapter."""
    adapter = ConcreteAdapter()
    messages = [{"role": "user", "content": "hello"}]
    assert adapter.sanitize_messages(messages) == messages

    kwargs: Any = {"model": "test", "temperature": 0.7}
    assert adapter.prepare_kwargs(kwargs) == kwargs
    assert adapter.build_http_client(30.0) is None


def test_base_adapter_prepare_kwargs_records_otel_span_attributes(in_memory_spans: Any) -> None:
    """Verify prepare_kwargs sets gen_ai.request.model and gen_ai.system on recording spans."""
    adapter = ConcreteAdapter()
    tracer = otel_trace.get_tracer(__name__)
    profile = ModelProfile.model_validate_json(
        '{"provider": "openai", "model_name": "gpt-4o-mini", "tpm_limit": 100000, '
        '"rpm_limit": 60, "max_tokens": 4096, "temperature": 0.0}'
    )

    with tracer.start_as_current_span("test_llm_span"):
        kwargs: Any = {"model": "gpt-4o-mini"}
        result = adapter.prepare_kwargs(kwargs, config=profile)
        assert result == kwargs

    spans = in_memory_spans.get_finished_spans()
    assert len(spans) == 1
    attrs = dict(spans[0].attributes)
    assert attrs["gen_ai.request.model"] == "gpt-4o-mini"
    assert attrs["gen_ai.system"] == "openai"


@pytest.mark.parametrize("invalid_timeout", [0.0, -5.0])
def test_base_adapter_build_http_client_invalid_timeout_raises_app_exception(invalid_timeout: float) -> None:
    """Negative test: Verify build_http_client raises AppException when timeout <= 0."""
    adapter = ConcreteAdapter()
    with pytest.raises(AppException) as exc_info:
        adapter.build_http_client(invalid_timeout)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_base_adapter_strip_unsupported_constraints() -> None:
    """Verify constraint stripping and discriminator preservation in schemas."""
    adapter = ConcreteAdapter()

    class NestedUnionA(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        block_type: Literal["type_a"] = "type_a"
        title: str = Field(min_length=1, max_length=100)

    class NestedUnionB(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        block_type: Literal["type_b"] = "type_b"
        value: int = Field(ge=0, le=10)

    UnionBlock = Annotated[NestedUnionA | NestedUnionB, Field(discriminator="block_type")]

    class RootContainer(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        contextual_override: bool = False
        override_reason: str = ""
        items: list[UnionBlock]

    schema = adapter.prepare_structured_output(RootContainer)
    assert isinstance(schema, dict)

    # Contextual overrides are popped from properties and required
    if "properties" in schema:
        assert "contextual_override" not in schema["properties"]
        assert "override_reason" not in schema["properties"]

    assert "$defs" in schema
    defs = schema["$defs"]
    assert "NestedUnionA" in defs
    assert "required" in defs["NestedUnionA"]
    assert "block_type" in defs["NestedUnionA"]["required"]
    # minLength, maxLength stripped
    assert "minLength" not in defs["NestedUnionA"]["properties"]["title"]
    assert "maxLength" not in defs["NestedUnionA"]["properties"]["title"]


@pytest.mark.asyncio
async def test_get_redis_client_for_pacing_pytest_mock() -> None:
    """Verify get_redis_client_for_pacing returns in-memory pacing client in pytest environment."""
    client = await get_redis_client_for_pacing()
    assert client is not None
    res = await client.set("key", "val")
    assert res is True


@pytest.mark.asyncio
async def test_apply_provider_pacing_disabled_when_delay_zero() -> None:
    """Verify apply_provider_pacing returns immediately if delay is 0."""
    with patch("backend_v2.llm.adapters.base_adapter.get_settings") as mock_settings:
        mock_settings.return_value.pacing_delay_vertex_seconds = 0
        mock_settings.return_value.pacing_delay_ai_studio_seconds = 0
        mock_settings.return_value.pacing_delay_openai_seconds = 0
        mock_settings.return_value.pacing_delay_mock_seconds = 0

        # Should return without exception or sleep
        await apply_provider_pacing("unknown_provider")
        await apply_provider_pacing(LLMProviderName.VERTEX_AI.value)
        await apply_provider_pacing(LLMProviderName.AI_STUDIO.value)


@pytest.mark.parametrize("empty_provider", ["", "   "])
@pytest.mark.asyncio
async def test_apply_provider_pacing_empty_provider_raises_app_exception(empty_provider: str) -> None:
    """Negative test: Verify apply_provider_pacing raises AppException on empty/whitespace provider_name."""
    with pytest.raises(AppException) as exc_info:
        await apply_provider_pacing(empty_provider)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_apply_provider_pacing_negative_rpm_limit_raises_app_exception() -> None:
    """Negative boundary test: Verify apply_provider_pacing raises AppException when rpm_limit < 0."""
    with pytest.raises(AppException) as exc_info:
        await apply_provider_pacing(LLMProviderName.OPENAI.value, rpm_limit=-1)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_apply_provider_pacing_with_rpm_limit() -> None:
    """Verify apply_provider_pacing computes delay from rpm_limit and acquires lock."""
    mock_redis = AsyncMock()
    mock_redis.set.return_value = True

    with patch("backend_v2.llm.adapters.base_adapter.get_redis_client_for_pacing", return_value=mock_redis):
        await apply_provider_pacing(LLMProviderName.OPENAI.value, strategy_id="fast", rpm_limit=60)
        mock_redis.set.assert_called_once_with("lock:pacer:openai:fast", "locked", nx=True, px=1000)


@pytest.mark.asyncio
async def test_apply_provider_pacing_poll_loop() -> None:
    """Verify apply_provider_pacing polls until lock acquired."""
    mock_redis = AsyncMock()
    # First call fails (lock held), second succeeds
    mock_redis.set.side_effect = [False, True]

    with patch("backend_v2.llm.adapters.base_adapter.get_redis_client_for_pacing", return_value=mock_redis):
        with patch("backend_v2.llm.adapters.base_adapter.get_settings") as mock_settings:
            mock_settings.return_value.pacing_delay_mock_seconds = 0.5
            mock_settings.return_value.context_cache_lock_poll_interval_ms = 500
            with patch("backend_v2.llm.adapters.base_adapter.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await apply_provider_pacing(LLMProviderName.MOCK.value)
                assert mock_redis.set.call_count == 2
                mock_sleep.assert_called_once_with(0.5)


@pytest.mark.asyncio
async def test_apply_provider_pacing_error_handling() -> None:
    """Verify apply_provider_pacing raises AppException on Redis error."""
    mock_redis = AsyncMock()
    mock_redis.set.side_effect = RuntimeError("Redis down")

    with patch("backend_v2.llm.adapters.base_adapter.get_redis_client_for_pacing", return_value=mock_redis):
        with patch("backend_v2.llm.adapters.base_adapter.get_settings") as mock_settings:
            mock_settings.return_value.pacing_delay_openai_seconds = 1.0
            mock_settings.return_value.context_cache_lock_poll_interval_ms = 500
            with pytest.raises(AppException) as exc_info:
                await apply_provider_pacing(LLMProviderName.OPENAI.value)
            assert "Pacing failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_redis_client_for_pacing_production_branch() -> None:
    """Verify get_redis_client_for_pacing initializes pool when not in test mode."""
    with patch.dict("backend_v2.llm.adapters.base_adapter.os.environ", {}, clear=True):
        with patch("backend_v2.llm.adapters.base_adapter.create_pool", new_callable=AsyncMock) as mock_create:
            mock_pool = AsyncMock()
            mock_create.return_value = mock_pool
            with patch("backend_v2.llm.adapters.base_adapter._redis_pool", None):
                pool = await get_redis_client_for_pacing()
                assert pool == mock_pool
                mock_create.assert_called_once()

                # Second call reuses existing pool
                pool2 = await get_redis_client_for_pacing()
                assert pool2 == mock_pool


@pytest.mark.asyncio
async def test_get_redis_client_for_pacing_init_failure() -> None:
    """Verify get_redis_client_for_pacing raises AppException on connection failure."""
    with patch.dict("backend_v2.llm.adapters.base_adapter.os.environ", {}, clear=True):
        with patch(
            "backend_v2.llm.adapters.base_adapter.create_pool", side_effect=RuntimeError("Redis connection error")
        ):
            with patch("backend_v2.llm.adapters.base_adapter._redis_pool", None):
                with pytest.raises(AppException) as exc_info:
                    await get_redis_client_for_pacing()
                assert "Redis initialization failed" in str(exc_info.value)


def test_base_adapter_strip_unsupported_constraints_list_and_explicit_discriminator() -> None:
    """Verify _strip_unsupported_constraints handles lists of schemas and explicit discriminator mappings."""
    adapter = ConcreteAdapter()
    schema_list: list[Any] = [
        {"minLength": 5, "const": "fixed_val"},
        {
            "discriminator": {"propertyName": "custom_tag"},
            "properties": {"custom_tag": {"type": "string"}},
            "required": ["contextual_override", "override_reason"],
        },
    ]

    adapter._strip_unsupported_constraints(schema_list)
    assert "minLength" not in schema_list[0]
    assert schema_list[0]["enum"] == ["fixed_val"]
    required_list = schema_list[1]["required"]
    assert isinstance(required_list, list)
    assert "custom_tag" in required_list
    assert "contextual_override" not in required_list
    assert "override_reason" not in required_list


def test_base_adapter_estimate_static_tokens() -> None:
    """Verify estimate_static_tokens correctly handles string, list blocks, and system exclusion."""
    adapter = ConcreteAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content="System instruction 16c"),  # 22 chars
            LLMMessageDTO(role="user", content="User static content 24c"),  # 23 chars
            LLMMessageDTO(role="assistant", content=[{"type": "text", "text": "Block text 1234"}]),
        ],
        dynamic_messages=[
            LLMMessageDTO(role="user", content="Dynamic text"),
        ],
    )

    # With exclude_system=False
    tokens_all, has_non_sys = adapter.estimate_static_tokens(prompt, exclude_system=False)
    assert has_non_sys is True
    assert tokens_all > 0

    # With exclude_system=True
    tokens_no_sys, has_non_sys_2 = adapter.estimate_static_tokens(prompt, exclude_system=True)
    assert has_non_sys_2 is True
    assert tokens_no_sys < tokens_all

    # System only prompt
    sys_only_prompt = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content="Only system message"),
        ],
        dynamic_messages=[],
    )
    tokens_sys_only, has_non_sys_3 = adapter.estimate_static_tokens(sys_only_prompt, exclude_system=True)
    assert has_non_sys_3 is False
    assert tokens_sys_only == 0
