"""Unit tests for AliasRegistry deterministic MCP tool namespace prefixing and parsing."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.mcp.alias_registry import AliasRegistry


def test_build_and_parse_namespaced_tool_alias_bijective_roundtrip() -> None:
    """Verify build_namespaced_tool_alias and parse_namespaced_tool_alias form a bijective roundtrip."""
    alias = AliasRegistry.build_namespaced_tool_alias("default_mcp_gateway", "mcp_tavily_search")
    assert alias == "default_mcp_gateway__mcp_tavily_search"

    parsed = AliasRegistry.parse_namespaced_tool_alias(alias)
    assert parsed.gateway_slug == "default_mcp_gateway"
    assert parsed.tool_id == "mcp_tavily_search"


def test_parse_namespaced_tool_alias_preserves_double_underscore_inside_tool_id() -> None:
    """Verify splitting occurs strictly on the first '__' delimiter, preserving '__' inside tool_id."""
    alias = AliasRegistry.build_namespaced_tool_alias("brave_gw", "v2__web__search")
    assert alias == "brave_gw__v2__web__search"

    parsed = AliasRegistry.parse_namespaced_tool_alias(alias)
    assert parsed.gateway_slug == "brave_gw"
    assert parsed.tool_id == "v2__web__search"


@pytest.mark.parametrize(
    ("invalid_slug", "tool_id"),
    [
        ("", "search"),
        ("   ", "search"),
        ("Invalid_Upper", "search"),
        ("bad__slug", "search"),
        ("_leading_underscore", "search"),
        ("trailing_underscore_", "search"),
        ("hyphen-slug", "search"),
    ],
)
def test_build_namespaced_tool_alias_invalid_gateway_slug_raises_app_exception(
    invalid_slug: str,
    tool_id: str,
) -> None:
    """Verify build_namespaced_tool_alias fails-fast with VALIDATION_FAILED on malformed gateway_slug."""
    with pytest.raises(AppException) as exc_info:
        AliasRegistry.build_namespaced_tool_alias(invalid_slug, tool_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize("empty_tool_id", ["", "   "])
def test_build_namespaced_tool_alias_empty_tool_id_raises_app_exception(empty_tool_id: str) -> None:
    """Verify build_namespaced_tool_alias fails-fast with VALIDATION_FAILED when tool_id is empty."""
    with pytest.raises(AppException) as exc_info:
        AliasRegistry.build_namespaced_tool_alias("default_mcp_gateway", empty_tool_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize(
    "malformed_alias",
    [
        "",
        "unnamespaced_tool_only",
        "__missing_gateway_slug",
        "default_mcp_gateway__",
        "default_mcp_gateway__   ",
        "Upper_Slug__tool_name",
        "hyphen-slug__tool_name",
        "_leading__tool_name",
    ],
)
def test_parse_namespaced_tool_alias_malformed_input_raises_app_exception(malformed_alias: str) -> None:
    """Verify parse_namespaced_tool_alias fails-fast with VALIDATION_FAILED on malformed alias strings."""
    with pytest.raises(AppException) as exc_info:
        AliasRegistry.parse_namespaced_tool_alias(malformed_alias)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
