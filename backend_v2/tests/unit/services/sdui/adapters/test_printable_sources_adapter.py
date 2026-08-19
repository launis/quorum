"""Unit tests for the PrintableSourcesAdapter."""

import pytest

from backend_v2.models.v2_core import I18nText, MCPAuditTrace, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import MarkdownBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.printable_sources_adapter import (
    PrintableSourcesAdapter,
)


@pytest.fixture
def valid_output_profile_fixture() -> OutputProfile:
    """Fixture for a valid output profile to use in tests."""
    return OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        content_blocks=[],
        target_block_order=[],
    )


def test_build_empty_profile_cache_returns_empty(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: empty profile_cache returns []."""
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert blocks == []


def test_build_empty_cited_sources_returns_empty(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: empty cited_sources returns []."""
    cache = RenderedSynthesisCache(
        cited_sources=[],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert blocks == []


def test_build_formats_cited_sources_as_markdown(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: formats cited_sources as markdown."""
    cache = RenderedSynthesisCache(
        cited_sources=["Source 1", "Source 2"],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "- Source 1\n- Source 2"


def test_build_preserves_existing_bullet_prefix(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: preserves existing bullet prefix."""
    cache = RenderedSynthesisCache(
        cited_sources=["- Source 1", "Source 2"],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "- Source 1\n- Source 2"


def test_build_ep_valid_http_source(valid_output_profile_fixture: OutputProfile) -> None:
    """EP (Valid HTTP Source): Add a test where a cited source contains 'http' to verify cited_urls tracking."""
    cache = RenderedSynthesisCache(
        cited_sources=["- https://example.com/source1", "Plain text source"],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    assert "- https://example.com/source1" in blocks[0].text
    assert "- Plain text source" in blocks[0].text


def test_build_ep_mcp_audit_traces(valid_output_profile_fixture: OutputProfile) -> None:
    """EP (MCP Audit Traces): Mock mcp_audit_map containing traces with source_urls to verify correct extraction."""
    mcp_audit_map = {
        "trace_1": MCPAuditTrace(
            tool_id="test_tool",
            step_name="test_step",
            query="test_query",
            source_urls=["https://mcp.example.com/doc1", "https://mcp.example.com/doc2"],
        )
    }
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=mcp_audit_map,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    assert "- https://mcp.example.com/doc1" in blocks[0].text
    assert "- https://mcp.example.com/doc2" in blocks[0].text


def test_build_bva_duplicate_prevention(valid_output_profile_fixture: OutputProfile) -> None:
    """BVA (Duplicate Prevention): Provide source_urls in the MCP map that already exist in cited_urls to ensure duplicates are filtered out."""
    cache = RenderedSynthesisCache(
        cited_sources=["- https://shared.example.com/doc"],
    )
    mcp_audit_map = {
        "trace_1": MCPAuditTrace(
            tool_id="test_tool",
            step_name="test_step",
            query="test_query",
            source_urls=["https://shared.example.com/doc", "https://unique.example.com/doc"],
        )
    }
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=mcp_audit_map,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    # The duplicated URL should only appear once
    assert blocks[0].text.count("https://shared.example.com/doc") == 1
    assert "- https://unique.example.com/doc" in blocks[0].text


def test_build_whitespace_and_empty_strings_in_sources_filtered(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """Boundary: empty strings and whitespace-only items in cited_sources are ignored."""
    cache = RenderedSynthesisCache(
        cited_sources=["   ", "", "Valid Source"],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "- Valid Source"
