"""Unit tests for BaseLLMAdapter abstract class and rate pacing logic."""

from typing import Annotated, Any, Literal
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException
from backend_v2.llm.adapters.base_adapter import (
    BaseLLMAdapter,
    apply_provider_pacing,
    get_redis_client_for_pacing,
)
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.enums import LLMProviderName
from backend_v2.models.prompt import CompiledPrompt


class ConcreteAdapter(BaseLLMAdapter):
    """Concrete implementation for testing base adapter defaults."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return compiled_prompt.to_flat_messages(), {}

    async def teardown_cache(self, workflow_run_id: str) -> None:
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        return usage

    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        return {}

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        schema = response_model.model_json_schema()
        self._strip_unsupported_constraints(schema)
        return schema


def test_base_adapter_defaults() -> None:
    """Verify default implementations of non-abstract methods in BaseLLMAdapter."""
    adapter = ConcreteAdapter()
    messages = [{"role": "user", "content": "hello"}]
    assert adapter.sanitize_messages(messages) == messages

    kwargs = {"model": "test", "temperature": 0.7}
    assert adapter.prepare_kwargs(kwargs) == kwargs
    assert adapter.build_http_client(30.0) is None


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
    assert "contextual_override" not in schema.get("properties", {})
    assert "override_reason" not in schema.get("properties", {})

    defs = schema.get("$defs", {})
    assert "NestedUnionA" in defs
    assert "block_type" in defs["NestedUnionA"].get("required", [])
    # minLength, maxLength stripped
    assert "minLength" not in defs["NestedUnionA"]["properties"]["title"]
    assert "maxLength" not in defs["NestedUnionA"]["properties"]["title"]


@pytest.mark.asyncio
async def test_get_redis_client_for_pacing_pytest_mock() -> None:
    """Verify get_redis_client_for_pacing returns mock in pytest environment."""
    client = await get_redis_client_for_pacing()
    assert client is not None
    res = await client.set("key", "val")
    assert res is True


@pytest.mark.asyncio
async def test_apply_provider_pacing_disabled_when_delay_zero() -> None:
    """Verify apply_provider_pacing returns immediately if delay is 0."""
    with patch("backend_v2.llm.adapters.base_adapter.get_settings") as mock_settings:
        mock_settings.return_value.pacing_delay_vertex_seconds = 0
        mock_settings.return_value.pacing_delay_openai_seconds = 0
        mock_settings.return_value.pacing_delay_mock_seconds = 0

        # Should return without exception or sleep
        await apply_provider_pacing("unknown_provider")
        await apply_provider_pacing(LLMProviderName.VERTEX_AI.value)


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
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
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
            with pytest.raises(AppException) as exc_info:
                await apply_provider_pacing(LLMProviderName.OPENAI.value)
            assert "Pacing failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_redis_client_for_pacing_production_branch() -> None:
    """Verify get_redis_client_for_pacing initializes pool when not in test mode."""
    with patch.dict("os.environ", {}, clear=True):
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
    with patch.dict("os.environ", {}, clear=True):
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
    schema_list = [
        {"minLength": 5, "const": "fixed_val"},
        {
            "discriminator": {"propertyName": "custom_tag"},
            "properties": {"custom_tag": {"type": "string"}},
        },
    ]

    adapter._strip_unsupported_constraints(schema_list)
    assert "minLength" not in schema_list[0]
    assert schema_list[0]["enum"] == ["fixed_val"]
    assert "custom_tag" in schema_list[1]["required"]
