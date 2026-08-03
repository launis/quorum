"""Unit tests for the PrintableSourcesAdapter."""

import pytest

from backend_v2.models.v2_core import I18nText, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import MarkdownBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.printable_sources_adapter import (
    PrintableSourcesAdapter,
)


@pytest.fixture
def valid_output_profile_fixture() -> OutputProfile:
    """Fixture for a valid output profile to use in tests."""
    return OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        workflow_id="wfw_test",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[],
    )


def test_build_empty_profile_cache_returns_empty(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: empty profile_cache returns []."""
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=None,
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
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=cache,
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
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=cache,
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
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=cache,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "- Source 1\n- Source 2"
