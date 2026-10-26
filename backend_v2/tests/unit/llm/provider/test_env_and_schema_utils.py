"""Unit tests for leaf environment, static reflection, MCP schema normalization, and diagnostic dump utilities."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import ConfigurationError
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
                type=JSONSchemaPropertyType.OBJECT,
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


def test_resolve_env_variables_missing_var_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify resolve_env_variables raises ConfigurationError when a referenced env variable is unset or empty."""
    monkeypatch.delenv("UNSET_SECRET_TOKEN_XYZ", raising=False)
    with pytest.raises(ConfigurationError) as exc_info:
        resolve_env_variables({"api_token": "${UNSET_SECRET_TOKEN_XYZ}"})
    assert "UNSET_SECRET_TOKEN_XYZ" in str(exc_info.value)

    monkeypatch.setenv("EMPTY_SECRET_TOKEN_XYZ", "")
    with pytest.raises(ConfigurationError) as empty_exc:
        resolve_env_variables({"api_token": "${EMPTY_SECRET_TOKEN_XYZ}"})
    assert "EMPTY_SECRET_TOKEN_XYZ" in str(empty_exc.value)


def test_safe_static_getattr_and_hasattr_across_types() -> None:
    """Verify _safe_static_getattr and _safe_static_hasattr handle None, properties, methods, and mappings."""
    assert _safe_static_getattr(None, "any_attr", "fallback") == "fallback"
    assert _safe_static_hasattr(None, "any_attr") is False

    sample = _SampleObject("quorum")
    assert _safe_static_getattr(sample, "value") == "quorum"
    assert _safe_static_getattr(sample, "computed_label") == "QUORUM"
    assert _safe_static_getattr(sample, "write_only_prop", "no_getter") == "no_getter"
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
