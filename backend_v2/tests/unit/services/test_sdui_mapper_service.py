from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.v2_core import (
    I18nText,
    MatrixScorecardRowDTO,
    MCPAuditTrace,
    ReportDataDTO,
    ReportLayoutDTO,
)
from backend_v2.models.view.sdui import (
    ScoreCardDisplay,
    SduiQuoteCard,
    SduiWarningCard,
    SectionType,
)
from backend_v2.services.sdui_mapper_service import SduiMapperService


def test_map_evidence_to_sdui_verified():
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"quote": "Verified quote.", "source_alias": "DOC-1"},
        context={"alias_registry": {"DOC-1": "opaque_1"}},
    )
    result = mapper.map_evidence_to_sdui(evidence)
    assert isinstance(result, SduiQuoteCard)
    assert result.quote == "Verified quote."
    assert result.source_aliases == ["opaque_1"]


def test_map_evidence_to_sdui_unverified():
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"quote": "Unverified quote.", "source_alias": "DOC-99"},
        context={"alias_registry": {"DOC-1": "opaque_1"}},
    )
    result = mapper.map_evidence_to_sdui(evidence, lang="en")
    assert isinstance(result, SduiWarningCard)
    assert "Hallucinated citations detected" in result.message


def test_map_report_to_sdui_complete():
    mapper = SduiMapperService()

    # Create dummy matrix row for scorecard
    row = MatrixScorecardRowDTO(
        block_id="blk_123",
        name="Security Policy",
        label_i18n=I18nText(default_locale="en", translations={"en": "Security Policy"}),
        score=85.0,
        scale_max=100.0,
        row_explanation="Policy is adequately documented.",
        is_evaluative=True,
    )

    # Create dummy layout
    layout = ReportLayoutDTO(
        preset_view="1d_metrics",
        title=I18nText(default_locale="en", translations={"en": "Metrics"}),
        axes=[row],
        synthesis_blocks=[{"block_type": "markdown", "text": "Layout synthesis"}],
    )

    # Create dummy audit trace
    audit_trace = MCPAuditTrace(
        tool_id="mcp_tavily",
        step_name="step_1",
        query="test query",
    )

    # Create dummy ReportDataDTO
    report = ReportDataDTO(
        execution_id="exe_123",
        workflow_id="wf_123",
        profile_id="prof_123",
        global_score=90.0,
        strictness_level=80,
        has_warning=True,
        content_blocks=[{"block_type": "markdown", "text": "Global content"}],
        layouts=[layout],
        mcp_tool_audit=[audit_trace],
        grouped_extensions={"metadata": ["test"]},
    )

    view = mapper.map_report_to_sdui(report, execution_id="exe_123")

    assert view.view_id == "exe_123"
    assert view.status_theme == "warning"
    assert view.metrics["global_score"] == 90.0
    assert view.metrics["strictness_level"] == 80

    # Sections: global content (1), layout scorecard (1), layout synthesis (1), mcp (1), extensions (1) -> total 5
    assert len(view.sections) == 5

    # Check Global Content
    assert view.sections[0].id == "global_content"
    assert view.sections[0].type == SectionType.MARKDOWN_BLOCK
    assert view.sections[0].data == [{"block_type": "markdown", "text": "Global content"}]

    # Check Layout Scorecard
    assert view.sections[1].id == "layout_scorecard_0"
    assert view.sections[1].type == SectionType.SCORE_CARD

    score_card = ScoreCardDisplay.model_validate(view.sections[1].data)
    assert score_card.dimensions[0].dimension_id == "blk_123"
    assert score_card.dimensions[0].dimension_label == "Security Policy"
    assert score_card.dimensions[0].score == 85.0
    assert score_card.dimensions[0].reasoning == "Policy is adequately documented."

    # Check Layout Synthesis
    assert view.sections[2].id == "layout_synthesis_0"
    assert view.sections[2].type == SectionType.MARKDOWN_BLOCK
    assert view.sections[2].data == [{"block_type": "markdown", "text": "Layout synthesis"}]

    # Check MCP
    assert view.sections[3].id == "xai_mcp_audit"
    assert view.sections[3].type == SectionType.USAGE_STATS

    # Check Extensions
    assert view.sections[4].id == "xai_extensions"
    assert view.sections[4].type == SectionType.USAGE_STATS


def test_map_report_to_sdui_empty():
    mapper = SduiMapperService()
    report = ReportDataDTO(
        execution_id="exe_123",
        workflow_id="wf_123",
        profile_id="prof_123",
        has_warning=False,
    )

    view = mapper.map_report_to_sdui(report, execution_id="exe_empty")

    assert view.view_id == "exe_empty"
    assert view.status_theme == "success"
    assert view.metrics == {}
    assert len(view.sections) == 0
