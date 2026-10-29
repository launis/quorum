"""Unit tests for MCP response summary sanitization within PrintableSourcesAdapter.

Verifies that raw CDATA tags, JSON dictionaries, and technical tool markers are strictly
sanitized before being rendered into SDUI MarkdownBlock components (TC-SAN-06).
"""

from __future__ import annotations

import pytest

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.enums import SourcesDisplayMode
from backend_v2.models.view.sdui import MarkdownBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.printable_sources_adapter import PrintableSourcesAdapter


@pytest.fixture
def base_sources_profile() -> OutputProfile:
    """Fixture providing a standard OutputProfile in VERIFIED_EVIDENCE mode."""
    return OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-sources-profile",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"fi": "Lähdeprofiili", "en": "Sources Profile"}),
        content_blocks=[],
        target_block_order=[],
        show_sources_summary_box=True,
        sources_display_mode=SourcesDisplayMode.VERIFIED_EVIDENCE,
    )


def test_printable_sources_sanitizes_tavily_cdata_json(base_sources_profile: OutputProfile) -> None:
    """TC-SAN-06: Verify real Tavily CDATA JSON trace is sanitized without raw CDATA or JSON syntax in SDUI."""
    raw_cdata_json = (
        '<![CDATA[\n{"query":"Työterveyslaitos Stanford etätyö","results":['
        '{"url":"https://www.ttl.fi/tutkimus","title":"Etätyö tutkimus",'
        '"content":"Työterveyslaitoksen ja Stanfordin tutkimus vahvistaa etätyön lisäävän työn hallinnan tunnetta."}]}\n]]>'
    )
    trace = MCPAuditTrace(
        id="aud_0195f3a0000070018111222233334444",
        tool_id="tavily_search",
        gateway_slug="search",
        namespaced_alias="search__tavily_search",
        step_name="faktantarkistus",
        claim_text="Etätyö parantaa hallinnan tunnetta.",
        query="Työterveyslaitos Stanford etätyö",
        response_summary=raw_cdata_json,
        source_urls=["https://www.ttl.fi/tutkimus"],
    )
    cache = RenderedSynthesisCache(cited_sources=[])
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map={trace.id: trace},
        global_score=None,
        profile=base_sources_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )

    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) >= 1
    markdown_block = blocks[0]
    assert isinstance(markdown_block, MarkdownBlock)
    text = markdown_block.text

    # Strict presentation assertions: zero technical artifacts
    assert "<![CDATA[" not in text
    assert "]]>" not in text
    assert '{"query"' not in text
    assert '{"url"' not in text
    assert "Työterveyslaitoksen ja Stanfordin tutkimus vahvistaa" in text


def test_printable_sources_sanitizes_plain_text_cdata(base_sources_profile: OutputProfile) -> None:
    """Positive: verify plain text in CDATA envelope is stripped cleanly in SDUI MarkdownBlock."""
    raw_text = "<![CDATA[Faktalähde: Työterveyslaitos on suomalainen tutkimuslaitos.]]>"
    trace = MCPAuditTrace(
        id="aud_0195f3a0000070028222333344445555",
        tool_id="wikipedia_search",
        gateway_slug="encyclopedia",
        namespaced_alias="encyclopedia__wikipedia_search",
        step_name="tietolahteet",
        claim_text="Työterveyslaitos tekee työelämän tutkimusta.",
        query="Työterveyslaitos",
        response_summary=raw_text,
        source_urls=["https://fi.wikipedia.org/wiki/Ty%C3%B6terveyslaitos"],
    )
    cache = RenderedSynthesisCache(cited_sources=[])
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map={trace.id: trace},
        global_score=None,
        profile=base_sources_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )

    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) >= 1
    markdown_block = blocks[0]
    assert isinstance(markdown_block, MarkdownBlock)
    text = markdown_block.text

    assert "<![CDATA[" not in text
    assert "]]>" not in text
    assert "Faktalähde: Työterveyslaitos on suomalainen tutkimuslaitos." in text


def test_printable_sources_omits_empty_or_whitespace_summary(base_sources_profile: OutputProfile) -> None:
    """Negative: verify empty or whitespace CDATA does not render empty mcp_result_label bullet."""
    trace = MCPAuditTrace(
        id="aud_0195f3a0000070038333444455556666",
        tool_id="tavily_search",
        gateway_slug="search",
        namespaced_alias="search__tavily_search",
        step_name="faktat",
        claim_text="Väite ilman tulosta.",
        query="tyhjä haku",
        response_summary="<![CDATA[   \n  ]]>",
        source_urls=["https://example.com/source"],
    )
    cache = RenderedSynthesisCache(cited_sources=[])
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map={trace.id: trace},
        global_score=None,
        profile=base_sources_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )

    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) >= 1
    markdown_block = blocks[0]
    assert isinstance(markdown_block, MarkdownBlock)
    text = markdown_block.text

    assert "<![CDATA[" not in text
    # Should not have dangling empty result line
    assert "Ulkoinen havainto / MCP-haun tulos:\n" not in text
    assert "Ulkoinen havainto:\n" not in text
