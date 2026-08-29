"""Unit tests for the PrintableSourcesAdapter."""

import pytest

from backend_v2.models.enums import SourcesDisplayMode
from backend_v2.models.v2_core import I18nText, MCPAuditTrace, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import MarkdownBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.printable_sources_adapter import (
    PRINTABLE_SOURCES_RULES,
    PrintableSourcesAdapter,
)


@pytest.fixture
def valid_output_profile_fixture() -> OutputProfile:
    """Fixture for a valid output profile to use in tests."""
    return OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-profile",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        content_blocks=[],
        target_block_order=[],
        show_sources_summary_box=True,
        sources_display_mode=SourcesDisplayMode.VERIFIED_EVIDENCE,
    )


def test_build_empty_profile_cache_returns_empty(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: empty profile_cache and empty mcp_audit_map returns []."""
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
    """Boundary: empty cited_sources and empty mcp_audit_map returns []."""
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
    """Positive: formats cited_sources with summary box and Harvard entries."""
    cache = RenderedSynthesisCache(
        cited_sources=["Kahneman, D. (2011). Thinking, Fast and Slow.", "Tversky, A. (1974). Judgment under Uncertainty."],
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
    text = blocks[0].text
    assert "### Sources and Bibliography" in text
    assert "> [!NOTE]" in text
    assert "> **Source Material & Fact-Checking Audit**" in text
    assert "- Kahneman, D. (2011). Thinking, Fast and Slow." in text
    assert "- Tversky, A. (1974). Judgment under Uncertainty." in text


def test_build_preserves_existing_bullet_prefix_fi(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: localized in Finnish and strips duplicate bullet prefixes."""
    cache = RenderedSynthesisCache(
        cited_sources=["- Lähde 1", "Lähde 2"],
    )
    context = AdapterContext(
        execution=None,
        locale="fi",
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
    text = blocks[0].text
    assert "### Lähteet ja lähdeviitteet" in text
    assert "> **Lähdeaineiston ja faktantarkistuksen auditointi**" in text
    assert "- Lähde 1" in text
    assert "- Lähde 2" in text


def test_build_filters_sr_internal_keys(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: Filters out internal DAG step IDs (sr_... and _results)."""
    cache = RenderedSynthesisCache(
        cited_sources=["sr_123456_results", "sr_faktantarkistaja", "Legitimate Harvard Source (2024)"],
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
    text = blocks[0].text
    assert "sr_123456_results" not in text
    assert "sr_faktantarkistaja" not in text
    assert "- Legitimate Harvard Source (2024)" in text


def test_build_disabled_summary_box_omits_note(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: show_sources_summary_box=False omits summary box."""
    profile_without_box = valid_output_profile_fixture.model_copy(
        update={"show_sources_summary_box": False}
    )
    cache = RenderedSynthesisCache(
        cited_sources=["Author, A. (2020). Book Title."],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile_without_box,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    text = blocks[0].text
    assert "> [!NOTE]" not in text
    assert "- Author, A. (2020). Book Title." in text


def test_build_verified_evidence_mode_with_mcp_traces(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: VERIFIED_EVIDENCE mode formats tool badges, claim, evidence, and links."""
    mcp_audit_map = {
        "trace_1": MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="faktantarkistaja",
            claim_text="Yhtiön liikevaihto kasvoi 25 prosenttia.",
            query="Yhtiön liikevaihto kasvu 2024",
            response_summary="Tilinpäätöstiedotteen mukaan liikevaihto kasvoi 25,4 % vuonna 2024.",
            source_urls=["https://example.com/tilinpaatos2024"],
        )
    }
    context = AdapterContext(
        execution=None,
        locale="fi",
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
    text = blocks[0].text
    assert "### Lähteet ja lähdeviitteet" in text
    assert "> **Lähdeaineiston ja faktantarkistuksen auditointi**" in text
    assert "🌐 Tavily AI Search Gateway" in text
    assert "- **[https://example.com/tilinpaatos2024](https://example.com/tilinpaatos2024)**" in text
    assert "**Tila:** ✅ Vahvistettu tutkimusnäytöllä" in text
    assert "**Todennusmenetelmä:** 🌐 Tavily AI Search Gateway" in text
    assert '**Väite tekstissä:** "Yhtiön liikevaihto kasvoi 25 prosenttia."' in text
    assert "**Todennettu näyttö:** Tilinpäätöstiedotteen mukaan liikevaihto kasvoi 25,4 % vuonna 2024." in text


def test_build_simple_bibliography_mode(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: SIMPLE_BIBLIOGRAPHY mode sorts entries alphabetically without nested evidence."""
    simple_profile = valid_output_profile_fixture.model_copy(
        update={"sources_display_mode": SourcesDisplayMode.SIMPLE_BIBLIOGRAPHY}
    )
    cache = RenderedSynthesisCache(
        cited_sources=["Zeller, M. (2022). Machine Learning.", "Alpha, B. (2020). AI Foundations."],
    )
    mcp_audit_map = {
        "trace_1": MCPAuditTrace(
            tool_id="mcp_wikipedia_read",
            step_name="taustatieto",
            query="Machine learning wiki",
            source_urls=["https://en.wikipedia.org/wiki/Machine_learning"],
        )
    }
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=mcp_audit_map,
        global_score=None,
        profile=simple_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    text = blocks[0].text
    assert "### Sources and Bibliography" in text
    # Should be sorted alphabetically
    assert "- Alpha, B. (2020). AI Foundations." in text
    assert "- [https://en.wikipedia.org/wiki/Machine_learning](https://en.wikipedia.org/wiki/Machine_learning)" in text
    assert "- Zeller, M. (2022). Machine Learning." in text
    # No nested sub-bullets in simple mode
    assert "**Status:**" not in text
    assert "**Verification method:**" not in text


def test_build_starved_returns_empty(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: starved context returns []."""
    from backend_v2.models.dtos.trace import DataStarvationEvent

    cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens"),
        cited_sources=["Source 1"],
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


def test_printable_sources_rules_export() -> None:
    """Invariant: PRINTABLE_SOURCES_RULES dictionary exists and contains expected gateway mappings."""
    assert "mcp_tools" in PRINTABLE_SOURCES_RULES
    assert "mcp_tavily_search" in PRINTABLE_SOURCES_RULES["mcp_tools"]
    assert "mcp_wikipedia_search" in PRINTABLE_SOURCES_RULES["mcp_tools"]
    assert "mcp_wikipedia_read" in PRINTABLE_SOURCES_RULES["mcp_tools"]
    assert "mcp_pubmed_search" in PRINTABLE_SOURCES_RULES["mcp_tools"]
    assert "default_tool" in PRINTABLE_SOURCES_RULES

