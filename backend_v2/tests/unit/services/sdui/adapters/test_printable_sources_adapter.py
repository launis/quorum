"""Unit tests for the PrintableSourcesAdapter."""

import pytest

from backend_v2.models.enums import SourcesDisplayMode
from backend_v2.models.v2_core import (
    AllowedMCPTool,
    I18nText,
    MCPAuditTrace,
    OutputProfile,
    RenderedSynthesisCache,
)
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


def test_build_empty_profile_cache_without_summary_box_returns_empty(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """Boundary: empty profile_cache, empty mcp_audit_map, and show_sources_summary_box=False returns []."""
    profile_no_box = valid_output_profile_fixture.model_copy(update={"show_sources_summary_box": False})
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile_no_box,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert blocks == []


def test_build_empty_cited_sources_with_summary_box_renders_notice(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """Positive: empty cited_sources and empty mcp_audit_map with show_sources_summary_box=True renders notice."""
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
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    text = blocks[0].text
    assert "### Sources and Bibliography" in text
    assert "> [!NOTE]" in text
    assert "> **Source Material & Fact-Checking Audit**" in text
    assert "> - **Bibliographic references:** 0" in text
    assert "- No external bibliographic citations or fact-checking traces recorded in this execution." in text


def test_build_empty_cited_sources_without_summary_box_returns_empty(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """Boundary: empty cited_sources and empty mcp_audit_map with show_sources_summary_box=False returns []."""
    profile_no_box = valid_output_profile_fixture.model_copy(update={"show_sources_summary_box": False})
    cache = RenderedSynthesisCache(
        cited_sources=[],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile_no_box,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(context)
    assert blocks == []


def test_build_formats_cited_sources_as_markdown(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: formats cited_sources with summary box and Harvard entries."""
    cache = RenderedSynthesisCache(
        cited_sources=[
            "Kahneman, D. (2011). Thinking, Fast and Slow.",
            "Tversky, A. (1974). Judgment under Uncertainty.",
        ],
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
    assert "- **Kahneman, D. (2011). Thinking, Fast and Slow.**" in text
    assert "**Status:** Verified with research evidence" in text
    assert "**Verification method:** Peer-reviewed scientific literature & framework" in text
    assert "- **Tversky, A. (1974). Judgment under Uncertainty.**" in text


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
    assert "- **Lähde 1**" in text
    assert "- **Lähde 2**" in text
    assert "**Tila:** Vahvistettu tutkimusnäytöllä" in text


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
    assert "- **Legitimate Harvard Source (2024)**" in text


def test_build_disabled_summary_box_omits_note(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: show_sources_summary_box=False omits summary box."""
    profile_without_box = valid_output_profile_fixture.model_copy(update={"show_sources_summary_box": False})
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
    assert "- **Author, A. (2020). Book Title.**" in text


def test_build_verified_evidence_with_in_text_citation_match(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: matches in-text narrative sentences with cited literature authors."""
    from backend_v2.models.view.sdui import ParagraphBlock

    cache = RenderedSynthesisCache(
        cited_sources=[
            "Popper, K. (1959). The Logic of Scientific Discovery.",
            "Toulmin, S. (1958). The Uses of Argument.",
        ],
        section_syntheses={
            "executive_summary_block": [
                ParagraphBlock(
                    text="As Popper (1959) states in his falsification principle, hypotheses must define failure criteria."
                ),
                ParagraphBlock(text="According to Toulmin (1958), claims require backing."),
            ]
        },
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
    assert (
        '**Synthesis finding:** "As Popper (1959) states in his falsification principle, hypotheses must define failure criteria."'
        in text
    )
    assert '**Synthesis finding:** "According to Toulmin (1958), claims require backing."' in text
    assert "**Theoretical framework:** Scientific evaluation framework: Empirical falsifiability" in text
    assert "**Source observation:** No criteria-matching specification found in source material" in text


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
    assert "Tavily Search Gateway" in text
    assert "- **[https://example.com/tilinpaatos2024](https://example.com/tilinpaatos2024)**" in text
    assert "**Tila:** Vahvistettu tutkimusnäytöllä" in text
    assert "**Todennusmenetelmä:** Tavily Search Gateway" in text
    assert '**Synteesin arviointi:** "Yhtiön liikevaihto kasvoi 25 prosenttia."' in text
    assert "**Tieteellinen viitekehys:** Tilinpäätöstiedotteen mukaan liikevaihto kasvoi 25,4 % vuonna 2024." in text


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


def test_build_verified_evidence_with_matrix_quotes_and_custom_tool_gateway(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """Positive: VERIFIED_EVIDENCE formats dynamic MCP tool gateway and extracts matrix input quote."""
    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
    from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
    from backend_v2.models.enums import VisualIntent
    from backend_v2.models.v2_core import ExecutionStatus
    from backend_v2.models.view.sdui import ParagraphBlock

    atom = ScorecardAtomDTO(
        atom_id="tda_0123456789abcdef0123456789abcdef",
        level=1,
        level_name="Taso 1",
        claim_label="Test claim",
        extracted_facts={},
        exact_quotes=[
            QuoteEvidenceDTO.model_validate(
                {"quote": "Verbatim input document extract quote.", "source_alias": []},
                context={"alias_registry": {}},
            )
        ],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="",
            step_2_scan_source="",
            step_3_evaluate_anti_patterns="",
            step_4_final_conclusion="",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Reasoning",
        contextual_override=False,
        structural_location=None,
        chart_display_label="Label",
        visual_intent=VisualIntent.NEUTRAL,
        human_override=None,
    )

    mat_row = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef0123456789abcdef",
        name="Matrix Label",
        label_i18n=I18nText(translations={"en": "Matrix Label"}),
        row_explanation="Explanation text",
        evaluated_atoms=[atom],
        is_evaluative=True,
    )

    cache = RenderedSynthesisCache(
        cited_sources=["Popper, K. (1959). The Logic of Scientific Discovery."],
        section_syntheses={
            "executive_summary_block": [
                ParagraphBlock(
                    text="As Popper (1959) states in his falsification principle, hypotheses must define failure criteria."
                ),
            ]
        },
    )

    mcp_audit_map = {
        "trace_custom": MCPAuditTrace(
            tool_id="mcp_custom_retrieval_tool",
            step_name="custom_step",
            claim_text="Custom tool verified statement.",
            query="custom query text without url",
            response_summary="Summary from custom gateway.",
            source_urls=[],
        )
    }

    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=mcp_audit_map,
        parsed_matrices={"mat_1": mat_row},
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )

    blocks = PrintableSourcesAdapter.build(context)
    assert len(blocks) == 1
    text = blocks[0].text
    assert "Custom Retrieval Tool Gateway" in text
    assert "- **custom query text without url**" in text
    assert '**Synthesis finding:** "Custom tool verified statement."' in text
    assert "**Theoretical framework:** Summary from custom gateway." in text
    assert '**Source observation:** "Verbatim input document extract quote."' in text


def test_build_mcp_tools_map_localization(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: resolves localized tool names from context.mcp_tools_map for both fi and en."""
    mcp_audit_map = {
        "trace_1": MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="faktantarkistaja",
            claim_text="Kasvu 25 %.",
            query="kasvu",
            response_summary="Vahvistettu 25 %.",
            source_urls=["https://example.com"],
        )
    }
    mcp_tools_map = {
        "mcp_tavily_search": AllowedMCPTool(
            tool_id="mcp_tavily_search",
            name=I18nText(translations={"fi": "Tavily AI -haku", "en": "Tavily AI Search"}),
            description="Tavily search tool",
            input_schema={},
        )
    }
    # Test Finnish localization
    ctx_fi = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=mcp_audit_map,
        mcp_tools_map=mcp_tools_map,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks_fi = PrintableSourcesAdapter.build(ctx_fi)
    assert len(blocks_fi) == 1
    assert "Tavily AI -haku" in blocks_fi[0].text

    # Test English localization
    ctx_en = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=mcp_audit_map,
        mcp_tools_map=mcp_tools_map,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks_en = PrintableSourcesAdapter.build(ctx_en)
    assert len(blocks_en) == 1
    assert "Tavily AI Search" in blocks_en[0].text


def test_build_mcp_tools_map_fallback_missing_locale(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: tool name missing target locale falls back cleanly to English ('en')."""
    mcp_audit_map = {
        "trace_1": MCPAuditTrace(
            tool_id="mcp_pubmed_search",
            step_name="faktantarkistaja",
            claim_text="Medical claim",
            query="pubmed query",
            response_summary="PubMed verified",
            source_urls=["https://pubmed.ncbi.nlm.nih.gov"],
        )
    }
    mcp_tools_map = {
        "mcp_pubmed_search": AllowedMCPTool(
            tool_id="mcp_pubmed_search",
            name=I18nText(translations={"en": "PubMed Database"}),
            description="PubMed tool",
            input_schema={},
        )
    }
    ctx = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=mcp_audit_map,
        mcp_tools_map=mcp_tools_map,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(ctx)
    assert len(blocks) == 1
    assert "PubMed Database" in blocks[0].text


def test_printable_sources_rules_export() -> None:
    """Invariant: PRINTABLE_SOURCES_RULES dictionary exists and contains expected rule mappings."""
    assert "literature_source" in PRINTABLE_SOURCES_RULES
    assert "theory_evidence_map" in PRINTABLE_SOURCES_RULES
    assert "default_tool" in PRINTABLE_SOURCES_RULES
