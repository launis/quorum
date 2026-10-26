"""Unit tests for the PrintableSourcesAdapter."""

import pytest

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.system_config import AllowedMCPTool, MCPAuditTrace
from backend_v2.models.dtos.sdui_rules import PrintableSourcesRulesDTO
from backend_v2.models.enums import SourcesDisplayMode
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
    assert "> **Sources & Fact-Checking Audit**" in text
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
    assert "> **Sources & Fact-Checking Audit**" in text
    assert "- **Kahneman, D. (2011). Thinking, Fast and Slow.**" in text
    assert "**Status:** Verified with research evidence" in text
    assert "**Verification Method:** Peer-reviewed scientific literature & framework" in text
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
    """Negative: Filters internal DAG step IDs (sr_..., stp_..., and _results) preserving citations."""
    cache = RenderedSynthesisCache(
        cited_sources=[
            "sr_123456_results",
            "sr_faktantarkistaja",
            "- sr_bulleted_step",
            "stp_blueprint_stage",
            "- stp_coaching_protocol",
            "Popper, K. (1959). The Logic of Scientific Discovery.",
            "Legitimate Harvard Source (2024)",
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
    text = blocks[0].text
    assert "sr_123456_results" not in text
    assert "sr_faktantarkistaja" not in text
    assert "sr_bulleted_step" not in text
    assert "stp_blueprint_stage" not in text
    assert "stp_coaching_protocol" not in text
    assert "- **Popper, K. (1959). The Logic of Scientific Discovery.**" in text
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
    """Positive: verifies segregated citation section for input material citations."""
    from backend_v2.models.view.sdui import ParagraphBlock

    cache = RenderedSynthesisCache(
        cited_sources=[
            "Popper, K. (1959). The Logic of Scientific Discovery.",
            "Toulmin, S. (1958). The Uses of Argument.",
        ],
        section_syntheses={
            "executive_summary_block": [
                ParagraphBlock(
                    text=(
                        "As Popper (1959) states in his falsification principle, "
                        "hypotheses must define failure criteria."
                    )
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
    assert "#### Citations in Evaluated Material" in text
    assert "- **Popper, K. (1959). The Logic of Scientific Discovery.**" in text
    assert "- **Toulmin, S. (1958). The Uses of Argument.**" in text
    assert "**Status:** Verified with research evidence" in text
    assert "**Verification Method:** Peer-reviewed scientific literature & framework" in text


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
    assert '**Synteesin havainto:** "Yhtiön liikevaihto kasvoi 25 prosenttia."' in text
    assert "**Ulkoinen havainto:** Tilinpäätöstiedotteen mukaan liikevaihto kasvoi 25,4 % vuonna 2024." in text


def test_build_mcp_traces_unverified_when_no_urls_or_articles_found(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """Negative: MCP trace without URLs or with empty results renders unverified status."""
    mcp_audit_map = {
        "trace_empty": MCPAuditTrace(
            tool_id="mcp_wikipedia_search",
            step_name="faktantarkistaja",
            claim_text="Yrityksen perustamisvuosi oli 1888.",
            query="Yritys Perustamisvuosi 1888",
            response_summary="No Wikipedia articles found for query: 'Yritys Perustamisvuosi 1888'",
            source_urls=[],
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
    assert "**Tila:** Ei vahvistettu (ei osumia tietokannassa)" in text
    assert "**Ulkoinen havainto:** No Wikipedia articles found for query: 'Yritys Perustamisvuosi 1888'" in text
    assert "Vahvistettu tutkimusnäytöllä" not in text


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
    from backend_v2.models.enums import ExecutionStatus, VisualIntent
    from backend_v2.models.view.sdui import ParagraphBlock

    quote_payload = {"source_quotes": "Verbatim input document extract quote.", "source_alias": []}
    atom = ScorecardAtomDTO(
        atom_id="tda_0123456789abcdef0123456789abcdef",
        level=1,
        level_name="Taso 1",
        claim_label="Test claim",
        extracted_facts={},
        exact_quotes=[
            QuoteEvidenceDTO.model_validate(
                quote_payload,
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
                    text=(
                        "As Popper (1959) states in his falsification principle, "
                        "hypotheses must define failure criteria."
                    )
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
    assert "#### External Fact-Checking Gateways" in text
    assert "Custom Retrieval Tool Gateway" in text
    assert "- **custom query text without url**" in text
    assert "**Status:** Unverified (no matching records found)" in text
    assert '**Synthesis finding:** "Custom tool verified statement."' in text
    assert "**External finding:** Summary from custom gateway." in text
    assert "#### Citations in Evaluated Material" in text
    assert "- **Popper, K. (1959). The Logic of Scientific Discovery.**" in text
    # Invariant: Atom quotes from evaluated matrix must NEVER be falsely bound to cited authors
    assert "Verbatim input document extract quote." not in text


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

    # Test namespaced tool_id resolution via short_tool_id and fallback formatting
    namespaced_audit_map = {
        "trace_ns_1": MCPAuditTrace(
            tool_id="default_mcp_gateway__mcp_tavily_search",
            step_name="faktantarkistaja",
            claim_text="Kasvu 25 %.",
            query="kasvu",
            response_summary="Vahvistettu 25 %.",
            source_urls=["https://example.com"],
        ),
        "trace_ns_2": MCPAuditTrace(
            tool_id="custom_gw__mcp_arxiv_search",
            step_name="faktantarkistaja",
            claim_text="Arxiv paper.",
            query="arxiv",
            response_summary="Found paper.",
            source_urls=["https://arxiv.org/abs/1234.5678"],
        ),
    }
    ctx_ns = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=namespaced_audit_map,
        mcp_tools_map=mcp_tools_map,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks_ns = PrintableSourcesAdapter.build(ctx_ns)
    assert len(blocks_ns) == 1
    assert "Tavily AI Search" in blocks_ns[0].text
    assert "Arxiv Search Gateway" in blocks_ns[0].text


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
    """Invariant: PRINTABLE_SOURCES_RULES is a strongly typed PrintableSourcesRulesDTO with expected rules."""
    assert isinstance(PRINTABLE_SOURCES_RULES, PrintableSourcesRulesDTO)
    assert (
        PRINTABLE_SOURCES_RULES.literature_source.display_name_en == "Peer-reviewed scientific literature & framework"
    )
    assert PRINTABLE_SOURCES_RULES.default_tool.display_name_en == "External Information Retrieval Gateway"


def test_sdui_printable_sources_deterministic_framework_provenance(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """Positive: PrintableSourcesAdapter deterministically renders evaluation frameworks from parsed matrices."""
    from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO

    matrix = MatrixScorecardRowDTO(
        block_id="blk_cognitive_depth_001",
        name="Cognitive Depth",
        label_i18n=I18nText(translations={"en": "Cognitive Depth", "fi": "Kognitiivinen syvyys"}),
        score=85.0,
        scale_max=100.0,
        is_evaluative=True,
        row_explanation="Explanation",
        cited_source_title="Bloom, B. S. (Ed.). (1956). Taxonomy of Educational Objectives.",
        cited_source_url="https://en.wikipedia.org/wiki/Bloom%27s_taxonomy",
    )
    ctx = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        mcp_tools_map={},
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        parsed_matrices={"blk_cognitive_depth_001": matrix},
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(ctx)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    text = blocks[0].text
    assert "#### Scientific Evaluation Frameworks" in text
    assert (
        "- **Cognitive Depth**: Bloom, B. S. (Ed.). (1956). Taxonomy of Educational Objectives. - "
        "[https://en.wikipedia.org/wiki/Bloom%27s_taxonomy](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)" in text
    )


def test_sdui_printable_sources_same_surname_collision_partition(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """ISTQB Boundary: Prevents ontological conflation of same-surname authors (Benjamin vs Nicholas Bloom).

    Verifies that Quorum internal evaluation framework (Benjamin Bloom 1956 on cognitive depth)
    renders exclusively under Subsection A, while evaluated input document citation (Nicholas Bloom 2024
    on hybrid work) renders exclusively under Subsection C, with zero cross-contamination.
    """
    from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO

    # Internal scientific evaluation framework
    benjamin_bloom_framework = MatrixScorecardRowDTO(
        block_id="blk_bloom_cognitive_depth",
        name="Cognitive Depth",
        label_i18n=I18nText(translations={"en": "Cognitive Depth"}),
        is_evaluative=True,
        row_explanation="Taxonomy of educational and cognitive depth.",
        cited_source_title="Bloom, B. S. (Ed.). (1956). Taxonomy of Educational Objectives: Cognitive Domain.",
        cited_source_url="https://en.wikipedia.org/wiki/Bloom%27s_taxonomy",
    )

    # External citation extracted from evaluated user material
    nicholas_bloom_input_citation = "Bloom, N., Han, R., & Liang, J. (2024). Hybrid working from home improves retention without damaging performance. Nature."

    profile_cache = RenderedSynthesisCache(
        cited_sources=[nicholas_bloom_input_citation],
        section_syntheses={},
    )

    ctx = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        mcp_tools_map={},
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=profile_cache,
        parsed_matrices={"blk_bloom_cognitive_depth": benjamin_bloom_framework},
        user_name=None,
        org_name=None,
    )

    blocks = PrintableSourcesAdapter.build(ctx)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    text = blocks[0].text

    # Both subsections must be present and segregated
    assert "#### Scientific Evaluation Frameworks" in text
    assert "#### Citations in Evaluated Material" in text

    # Split text by section to verify partition isolation
    parts = text.split("#### ")
    frameworks_section = next(p for p in parts if p.startswith("Scientific Evaluation Frameworks"))
    citations_section = next(p for p in parts if p.startswith("Citations in Evaluated Material"))

    # Benjamin Bloom (1956) must exist EXCLUSIVELY in Frameworks
    assert "Bloom, B. S. (Ed.). (1956)" in frameworks_section
    assert "Bloom, B. S. (Ed.). (1956)" not in citations_section

    # Nicholas Bloom (2024) must exist EXCLUSIVELY in Input Citations
    assert "Bloom, N., Han, R., & Liang, J. (2024)" in citations_section
    assert "Bloom, N., Han, R., & Liang, J. (2024)" not in frameworks_section


def test_sdui_printable_sources_empty_framework_negative_partition(
    valid_output_profile_fixture: OutputProfile,
) -> None:
    """ISTQB Negative: Custom matrix lacking theory grounding does not render empty headers or error."""
    from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO

    matrix_no_grounding = MatrixScorecardRowDTO(
        block_id="blk_custom_lightweight",
        name="Custom Lightweight Step",
        label_i18n=I18nText(translations={"en": "Custom Lightweight Step"}),
        score=0.0,
        scale_max=100.0,
        is_evaluative=False,
        row_explanation="Custom prompt without academic citations",
        cited_source_title=None,
        cited_source_url=None,
    )

    # Subcase 1: Summary box disabled and no citations -> empty blocks
    profile_no_box = valid_output_profile_fixture.model_copy(update={"show_sources_summary_box": False})
    ctx_empty = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        mcp_tools_map={},
        global_score=None,
        profile=profile_no_box,
        profile_cache=None,
        parsed_matrices={"blk_custom": matrix_no_grounding},
        user_name=None,
        org_name=None,
    )
    blocks = PrintableSourcesAdapter.build(ctx_empty)
    assert blocks == []

    # Subcase 2: Summary box enabled -> renders graceful notice, zero broken headers
    ctx_box = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        mcp_tools_map={},
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        parsed_matrices={"blk_custom": matrix_no_grounding},
        user_name=None,
        org_name=None,
    )
    blocks_box = PrintableSourcesAdapter.build(ctx_box)
    assert len(blocks_box) == 1
    assert isinstance(blocks_box[0], MarkdownBlock)
    text_box = blocks_box[0].text
    assert "> **Sources & Fact-Checking Audit**" in text_box
    assert "No external bibliographic citations or fact-checking traces recorded in this execution." in text_box
    assert "#### " not in text_box
