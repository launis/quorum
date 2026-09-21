from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
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
        label_i18n=I18nText(translations={"en": "Security Policy"}),
        score=85.0,
        scale_max=100.0,
        row_explanation="Policy is adequately documented.",
        is_evaluative=True,
    )

    # Create dummy layout
    layout = SduiMetrics1DBlock(
        title=I18nText(translations={"en": "Metrics"}),
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
    assert view.metrics.global_score == 90.0
    assert view.metrics.strictness_level == 80.0

    # Check SDUI Blocks
    assert len(view.inner_sdui_blocks) == 1
    assert view.inner_sdui_blocks[0].title is not None
    assert view.inner_sdui_blocks[0].title.translations["en"] == "Metrics"
    assert view.inner_sdui_blocks[0].axes[0].name == "Security Policy"


def test_map_report_to_sdui_na_outcomes() -> None:
    from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
    from backend_v2.models.enums import ExecutionStatus, SDUIComponentType
    from backend_v2.models.view.sdui import SduiNACard

    mapper = SduiMapperService()
    na_result = AtomResultDTO(
        tda_id="tda_1",
        status=ExecutionStatus.N_A,
        short_circuit_reason_tda_ids=["tda_1"],
    )
    report = ReportDataDTO(
        execution_id="exe_na",
        workflow_id="wf_na",
        profile_id="prof_na",
        results=[na_result],
        hydrated_references={
            "tda_1": HydratedAtomDTO(
                sdui_component=SDUIComponentType.N_A_CARD,
                resolved_claim="Requirement not applicable for this sector",
            )
        },
    )
    view = mapper.map_report_to_sdui(report, execution_id="exe_na")
    assert len(view.inner_sdui_blocks) == 1
    assert isinstance(view.inner_sdui_blocks[0], SduiNACard)
    assert view.inner_sdui_blocks[0].short_circuit_reason_tda_ids == ["tda_1"]
    assert "Requirement not applicable for this sector" in view.inner_sdui_blocks[0].message



