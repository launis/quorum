"""Unit tests for leaf environment, static reflection, MCP schema normalization, and diagnostic dump utilities."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import litellm
import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import ConfigurationError
from backend_v2.llm.provider import LiteLLMProvider, get_settings
from backend_v2.llm.provider.env_and_schema_utils import (
    _INTERNAL_NON_API_KEYS,
    _normalize_mcp_tool_schema_for_llm,
    _safe_static_getattr,
    _safe_static_hasattr,
    _sync_diagnostic_dump,
    resolve_env_variables,
)
from backend_v2.models.dtos.mcp import (
    MCPFunctionDefinitionDTO,
    MCPToolDeclarationDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.enums import JSONSchemaPropertyType


class _SampleObject:
    """Helper class for testing static attribute and property inspection."""

    def __init__(self, value: str) -> None:
        """Initialize helper with a value.

        Args:
            value: String attribute value.
        """
        self.value = value

    @property
    def computed_label(self) -> str:
        """Return uppercase value.

        Returns:
            Uppercase string.
        """
        return self.value.upper()

    write_only_prop = property(fget=None)

    @property
    def broken_prop(self) -> str:
        """Raise AttributeError during property evaluation to exercise static fallback."""
        raise AttributeError("broken attribute inside property")

    def greet(self) -> str:
        """Return a formatted greeting.

        Returns:
            Greeting string.
        """
        return f"hello {self.value}"


class _DummySchemaModel(BaseModel):
    """Strict Pydantic model for schema normalization testing."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    title: str


class _MockMessage:
    content = "test response"
    tool_calls: list[Any] = []


class _MockChoice:
    message = _MockMessage()
    finish_reason = "stop"


class _MockUsage:
    prompt_tokens = 10
    completion_tokens = 5
    total_tokens = 15


class _MockLiteLLMResponse:
    choices = [_MockChoice()]
    model_extra: Any = {}
    usage = _MockUsage()

    def model_dump(self) -> Any:
        return {}


def test_resolve_env_variables_and_mcp_schema_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify resolve_env_variables expands ${VAR} and _normalize_mcp_tool_schema_for_llm maps schema keys."""
    monkeypatch.setenv("TEST_VERTEX_LOCATION", "europe-west4")
    resolved = resolve_env_variables(
        {
            "vertex_location": "${TEST_VERTEX_LOCATION}",
            "static_param": "keep-as-is",
            "max_retries": 3,
        }
    )
    assert resolved == {
        "vertex_location": "europe-west4",
        "static_param": "keep-as-is",
        "max_retries": 3,
    }

    tool_dto = MCPToolDeclarationDTO(
        function=MCPFunctionDefinitionDTO(
            name="search_docs",
            description="Search indexed documents.",
            parameters=MCPToolInputSchemaDTO(
                type="object",
                properties={
                    "mode": MCPToolSchemaPropertyDTO(
                        type=JSONSchemaPropertyType.STRING,
                        description="Search mode.",
                        enum_values=["fast", "deep"],
                    )
                },
                required=["mode"],
                additional_properties=False,
            ),
        )
    )

    normalized = _normalize_mcp_tool_schema_for_llm([tool_dto, _DummySchemaModel(title="check"), 42])
    assert isinstance(normalized, list)
    first_tool = normalized[0]
    assert first_tool["function"]["parameters"]["additionalProperties"] is False
    assert "additional_properties" not in first_tool["function"]["parameters"]
    assert first_tool["function"]["parameters"]["properties"]["mode"]["enum"] == ["fast", "deep"]
    assert "enum_values" not in first_tool["function"]["parameters"]["properties"]["mode"]
    assert normalized[1] == {"title": "check"}
    assert normalized[2] == 42
    assert _INTERNAL_NON_API_KEYS == frozenset({"mock_identity", "validation_context"})


def test_resolve_env_variables_missing_var_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify resolve_env_variables logs error and raises ConfigurationError when env var is missing."""
    monkeypatch.delenv("UNSET_SECRET_TOKEN_XYZ", raising=False)
    with caplog.at_level(logging.ERROR), pytest.raises(ConfigurationError) as exc_info:
        resolve_env_variables({"api_token": "${UNSET_SECRET_TOKEN_XYZ}"})
    assert "UNSET_SECRET_TOKEN_XYZ" in str(exc_info.value)
    assert "UNSET_SECRET_TOKEN_XYZ" in caplog.text

    caplog.clear()
    monkeypatch.setenv("EMPTY_SECRET_TOKEN_XYZ", "")
    with caplog.at_level(logging.ERROR), pytest.raises(ConfigurationError) as empty_exc:
        resolve_env_variables({"api_token": "${EMPTY_SECRET_TOKEN_XYZ}"})
    assert "EMPTY_SECRET_TOKEN_XYZ" in str(empty_exc.value)
    assert "EMPTY_SECRET_TOKEN_XYZ" in caplog.text


def test_safe_static_getattr_and_hasattr_across_types() -> None:
    """Verify _safe_static_getattr and _safe_static_hasattr handle None, properties, methods, and mappings."""
    assert _safe_static_getattr(None, "any_attr", "fallback") == "fallback"
    assert _safe_static_hasattr(None, "any_attr") is False

    sample = _SampleObject("quorum")
    assert _safe_static_getattr(sample, "value") == "quorum"
    assert _safe_static_getattr(sample, "computed_label") == "QUORUM"
    assert _safe_static_getattr(sample, "write_only_prop", "no_getter") == "no_getter"
    assert _safe_static_getattr(sample, "broken_prop", "attr_err_fallback") == "attr_err_fallback"
    bound_method = _safe_static_getattr(sample, "greet")
    assert callable(bound_method)
    assert bound_method() == "hello quorum"
    assert _safe_static_getattr(sample, "missing_attr", "default_val") == "default_val"

    assert _safe_static_hasattr(sample, "value") is True
    assert _safe_static_hasattr(sample, "computed_label") is True
    assert _safe_static_hasattr(sample, "missing_attr") is False

    mapping_target = {"status_code": 429, "nested": "ok"}
    assert _safe_static_getattr(mapping_target, "status_code") == 429
    assert _safe_static_getattr(mapping_target, "absent_key", 200) == 200
    assert _safe_static_hasattr(mapping_target, "status_code") is True
    assert _safe_static_hasattr(mapping_target, "absent_key") is False

    assert _safe_static_getattr(12345, "non_existent", "num_default") == "num_default"
    assert _safe_static_hasattr(12345, "non_existent") is False


def test_sync_diagnostic_dump_writes_and_handles_os_error(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify _sync_diagnostic_dump appends diagnostic content and logs OSError on invalid path."""
    dump_path = tmp_path / "diagnostic_prompts.log"
    _sync_diagnostic_dump(str(dump_path), "openai/gpt-5.1", '{"role": "user", "content": "hi"}')

    written = dump_path.read_text(encoding="utf-8")
    assert "--- openai/gpt-5.1 ---" in written
    assert '{"role": "user", "content": "hi"}' in written

    # Passing a directory path instead of a file triggers OSError cleanly
    with caplog.at_level(logging.ERROR):
        _sync_diagnostic_dump(str(tmp_path), "openai/gpt-5.1", "payload")
    assert "Failed to dump prompt" in caplog.text


def test_resolve_env_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test resolving env variables with ${ENV_VAR} structure."""
    monkeypatch.setenv("TEST_REGION_VAR", "europe-west3")
    params = {"location": "${TEST_REGION_VAR}", "other": "constant"}
    resolved = resolve_env_variables(params)
    assert resolved["location"] == "europe-west3"
    assert resolved["other"] == "constant"

    with pytest.raises(ConfigurationError) as exc_info:
        resolve_env_variables({"location": "${MISSING_ENV_VAR_COGNITIVE}"})
    assert "MISSING_ENV_VAR_COGNITIVE" in str(exc_info.value)


def test_sync_diagnostic_dump(tmp_path: Path) -> None:
    """Test _sync_diagnostic_dump file writing and error handling."""
    dump_file = str(tmp_path / "dump.txt")
    _sync_diagnostic_dump(dump_file, "gemini-pro", "test prompt payload")

    content = (tmp_path / "dump.txt").read_text(encoding="utf-8")
    assert "--- gemini-pro ---" in content
    assert "test prompt payload" in content

    bad_path = str(tmp_path / "non_existent_folder" / "sub" / "dump.txt")
    _sync_diagnostic_dump(bad_path, "gemini-pro", "test prompt payload")


@pytest.mark.asyncio
async def test_lite_llm_provider_strips_internal_mock_identity_from_call_kwargs() -> None:
    """Verify LiteLLMProvider does not leak internal mock_identity into litellm router call_kwargs."""
    LiteLLMProvider._router_cache.clear()
    provider = LiteLLMProvider(
        model_name="openai/gpt-5.1",
        api_key="test-key",
        limits={"tpm": 100, "rpm": 10},
        settings=get_settings(),
    )
    provider.router.acompletion = AsyncMock(return_value=_MockLiteLLMResponse())
    await provider.generate(
        prompt="Hello",
        temperature=0.0,
        max_tokens=100,
        mock_identity="ExecutiveSummaryTask",
    )
    called_kwargs = provider.router.acompletion.call_args[1]
    assert "mock_identity" not in called_kwargs


@pytest.mark.asyncio
async def test_lite_llm_provider_strips_unpacked_internal_keys_from_call_kwargs() -> None:
    """Verify LiteLLMProvider purges unpacked internal keys from call_kwargs."""
    LiteLLMProvider._router_cache.clear()
    provider = LiteLLMProvider(
        model_name="openai/gpt-5.1",
        api_key="test-key",
        limits={"tpm": 100, "rpm": 10},
        settings=get_settings(),
    )
    provider.router.acompletion = AsyncMock(return_value=_MockLiteLLMResponse())
    unpacked_kwargs: Any = {
        "mock_identity": "DynamicTask",
        "validation_context": {"rule": 1},
    }
    await provider.generate(
        prompt="Hello",
        temperature=0.0,
        max_tokens=100,
        **unpacked_kwargs,
    )
    called_kwargs = provider.router.acompletion.call_args[1]
    assert "mock_identity" not in called_kwargs
    assert "validation_context" not in called_kwargs


@pytest.mark.asyncio
async def test_lite_llm_provider_serializes_mcp_tool_declarations_to_standard_json_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify LiteLLMProvider.generate maps enum_values and additional_properties to JSON Schema."""
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.001)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())

    LiteLLMProvider._router_cache.clear()
    provider = LiteLLMProvider(
        model_name="openai/gpt-5.4",
        api_key="test-key",
        limits={"tpm": 100, "rpm": 10},
        settings=get_settings(),
    )
    provider.router.acompletion = AsyncMock(return_value=_MockLiteLLMResponse())

    tool_decl = MCPToolDeclarationDTO(
        type="function",
        function=MCPFunctionDefinitionDTO(
            name="default_mcp_gateway__mcp_tavily_search",
            description="Search web via MCP",
            parameters=MCPToolInputSchemaDTO(
                properties={
                    "query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING, description="Search query"),
                    "search_depth": MCPToolSchemaPropertyDTO(
                        type=JSONSchemaPropertyType.STRING,
                        description="Depth",
                        enum_values=["basic", "advanced"],
                    ),
                    "filter_obj": MCPToolSchemaPropertyDTO(
                        type=JSONSchemaPropertyType.OBJECT,
                        properties={
                            "mode": MCPToolSchemaPropertyDTO(
                                type=JSONSchemaPropertyType.STRING,
                                enum_values=["strict", "relaxed"],
                            ),
                        },
                        additional_properties=False,
                    ),
                },
                required=["query"],
                additional_properties=False,
            ),
            strict=True,
        ),
    )

    await provider.generate(prompt="Run search", temperature=0.0, max_tokens=100, tools=[tool_decl])
    called_kwargs = provider.router.acompletion.call_args[1]
    params = called_kwargs["tools"][0]["function"]["parameters"]
    assert params["additionalProperties"] is False
    assert params["properties"]["search_depth"]["enum"] == ["basic", "advanced"]
    nested_obj = params["properties"]["filter_obj"]
    assert nested_obj["additionalProperties"] is False
    assert nested_obj["properties"]["mode"]["enum"] == ["strict", "relaxed"]
    assert _normalize_mcp_tool_schema_for_llm(None) is None
    assert _normalize_mcp_tool_schema_for_llm(42) == 42
