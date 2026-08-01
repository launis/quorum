from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.v2_core import (
    I18nText,
    MatrixScorecardRowDTO,
    MCPAuditTrace,
    ReportDataDTO,
)
from backend_v2.models.view.sdui import (
    SduiMetrics1DBlock,
    SduiQuoteCard,
    SduiWarningCard,
)
from backend_v2.services.sdui_mapper_service import SduiMapperService


def test_map_evidence_to_sdui_verified() -> None:
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"quote": "Verified quote.", "source_alias": "DOC-1"},
        context={"alias_registry": {"DOC-1": "opaque_1"}},
    )
    result = mapper.map_evidence_to_sdui(evidence)
    assert isinstance(result, SduiQuoteCard)
    assert result.quote == "Verified quote."
    assert result.source_aliases == ["opaque_1"]


def test_map_evidence_to_sdui_unverified() -> None:
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"quote": "Unverified quote.", "source_alias": "DOC-99"},
        context={"alias_registry": {"DOC-1": "opaque_1"}},
    )
    result = mapper.map_evidence_to_sdui(evidence, lang="en")
    assert isinstance(result, SduiWarningCard)
    assert "Hallucinated citations detected" in result.message


def test_map_report_to_sdui_complete() -> None:
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
    layout = SduiMetrics1DBlock(
        title=I18nText(default_locale="en", translations={"en": "Metrics"}),
        axes=[row],
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
        inner_sdui_blocks=[layout],
        mcp_tool_audit=[audit_trace],
    )

    view = mapper.map_report_to_sdui(report, execution_id="exe_123")

    assert view.view_id == "exe_123"
    assert view.status_theme == "warning"
    assert view.metrics is not None
    assert view.metrics["global_score"] == 90.0
    assert view.metrics["strictness_level"] == 80

    # Sections: mcp (1) -> total 1
    assert len(view.sections) == 1

    # Check SDUI Blocks
    assert len(view.inner_sdui_blocks) == 1
    assert view.inner_sdui_blocks[0].title.translations["en"] == "Metrics"
    assert view.inner_sdui_blocks[0].axes[0].name == "Security Policy"

    # Check MCP Audit Section
    assert view.sections[0].id == "xai_mcp_audit"
    assert view.sections[0].type.value == "USAGE_STATS"
    assert len(view.sections[0].data) == 1
    assert view.sections[0].data[0]["tool_id"] == "mcp_tavily"
