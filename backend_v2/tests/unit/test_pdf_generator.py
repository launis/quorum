"""Unit tests for PdfReportService Dumb Painter."""

from unittest.mock import MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    ParagraphBlock,
    SduiMatrixTableBlock,
    SduiMetadataBlock,
    SduiMetrics1DBlock,
    SduiQuadrantMatrixBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.pdf_generator import PdfReportService

_EXEC_ID_1 = "exe_0195f3a00000700a8aaaaaaabbbbbbbb"
_EXEC_ID_2 = "exe_0195f3a0000070018111111111111111"
_EXEC_ID_3 = "exe_0195f3a0000070028222222222222222"
_WF_ID = "wor_0195f3a0000070038333333333333333"
_PRF_ID = "prf_0195f3a0000070048444444444444444"
_BLK_ID = "blk_0195f3a0000070058555555555555555"


def _make_report_dto(
    execution_id: str,
    inner_sdui_blocks: list[AnySduiBlock],
    profile_name: I18nText | None = None,
) -> ReportDataDTO:
    """Construct a strictly typed ReportDataDTO instance for unit testing.

    Args:
        execution_id: Canonical execution Opaque Stripe ID.
        inner_sdui_blocks: List of SDUI blocks to render.
        profile_name: Optional localized profile name.

    Returns:
        Populated ReportDataDTO instance.
    """
    resolved_profile_name = profile_name
    if resolved_profile_name is None:
        resolved_profile_name = I18nText(translations={"en": "Test Profile", "fi": "Test Profile"})
    return ReportDataDTO(
        execution_id=execution_id,
        strictness_level=85,
        workflow_id=_WF_ID,
        profile_id=_PRF_ID,
        profile_name=resolved_profile_name,
        available_profiles={},
        inner_sdui_blocks=inner_sdui_blocks,
        results=[],
        hydrated_references={},
        visible_metadata=[],
        mcp_tool_audit=[],
    )


def _make_axis(evaluated_atoms: list[ScorecardAtomDTO]) -> MatrixScorecardRowDTO:
    """Construct a strictly typed MatrixScorecardRowDTO instance for unit testing.

    Args:
        evaluated_atoms: Evaluated scorecard atoms to attach to the row.

    Returns:
        Populated MatrixScorecardRowDTO instance.
    """
    return MatrixScorecardRowDTO(
        block_id=_BLK_ID,
        name="Test Axis",
        label_i18n=I18nText(translations={"en": "Test Axis", "fi": "Testi Akseli"}),
        description=None,
        score=None,
        raw_score=None,
        raw_scale_min=None,
        raw_scale_max=None,
        score_display_label="85%",
        scale_min=None,
        scale_max=None,
        normalized_score=None,
        true_atoms=None,
        total_atoms=None,
        row_explanation="All good",
        evidence_type=None,
        cited_source_id=None,
        cited_text_quote=None,
        cited_web_citation=None,
        cited_source_title=None,
        cited_source_url=None,
        confidence=None,
        inner_sdui_blocks=[],
        contextual_override=None,
        semantic_reasoning=None,
        level_breakdown={"1": "1/1"},
        level_names={"1": "Level 1"},
        ui_plot_ratio=0.85,
        ui_boundary_labels={},
        is_evaluative=True,
        allow_contextual_override=True,
        used_evidence_ids=[],
        evaluated_atoms=evaluated_atoms,
        clustered_row_sources=[],
        tda_state=None,
    )


@pytest.mark.asyncio
async def test_pdf_generator_chart_injection_failure_safe() -> None:
    """Verify PDF generation succeeds when inner SDUI blocks do not require static charts."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [SduiMetrics1DBlock(axes=[])])

    pdf_bytes = await svc.generate_execution_pdf(execution_id=_EXEC_ID_1, report_dto=dto, locale="en")
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)


@pytest.mark.asyncio
async def test_html_generator_chart_injection_failure_safe() -> None:
    """Verify HTML generation produces valid DOCTYPE document without charts."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [SduiMetrics1DBlock(axes=[])])

    html_string = await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="en")
    assert html_string is not None
    assert isinstance(html_string, str)
    assert html_string.strip().startswith("<!DOCTYPE html>")


@pytest.mark.asyncio
async def test_pdf_generator_radar_chart_rendering() -> None:
    """Verify radar chart base64 output is injected into generated HTML."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_2, [SduiRadarChartBlock(axes=[])])

    with patch("backend_v2.services.pdf_generator.generate_radar_chart", return_value="fake_radar_b64"):
        html = await svc.generate_execution_html(execution_id=_EXEC_ID_2, report_dto=dto, locale="fi")
        assert "fake_radar_b64" in html


@pytest.mark.asyncio
async def test_pdf_generator_empty_radar_chart_crashes() -> None:
    """Verify empty radar chart return value raises ConfigurationError fail-fast."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_2, [SduiRadarChartBlock(axes=[])])

    with patch("backend_v2.services.pdf_generator.generate_radar_chart", return_value=""):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_pdf(execution_id=_EXEC_ID_2, report_dto=dto, locale="en")
        assert "returned empty data for block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_scatter_plot_rendering() -> None:
    """Verify scatter plot base64 output is injected into generated HTML."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [SduiScatterPlotBlock(axes=[])])

    with patch("backend_v2.services.pdf_generator.generate_scatter_chart", return_value="fake_b64"):
        html = await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="fi")
        assert "fake_b64" in html


@pytest.mark.asyncio
async def test_pdf_generator_empty_scatter_plot_crashes() -> None:
    """Verify empty scatter chart return value raises ConfigurationError fail-fast."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [SduiScatterPlotBlock(axes=[])])

    with patch("backend_v2.services.pdf_generator.generate_scatter_chart", return_value=""):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_pdf(execution_id=_EXEC_ID_1, report_dto=dto, locale="fi")
        assert "generate_scatter_chart returned empty data for block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_quadrant_matrix_rendering() -> None:
    """Verify quadrant matrix chart base64 output is injected into generated HTML."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [SduiQuadrantMatrixBlock(axes=[])])

    with patch("backend_v2.services.pdf_generator.generate_quadrant_matrix_chart", return_value="fake_quadrant_b64"):
        html = await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="fi")
        assert "fake_quadrant_b64" in html


@pytest.mark.asyncio
async def test_pdf_generator_empty_quadrant_matrix_crashes() -> None:
    """Verify empty quadrant matrix chart return value raises ConfigurationError fail-fast."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [SduiQuadrantMatrixBlock(axes=[])])

    with patch("backend_v2.services.pdf_generator.generate_quadrant_matrix_chart", return_value=""):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_pdf(execution_id=_EXEC_ID_1, report_dto=dto, locale="fi")
        assert "generate_quadrant_matrix_chart returned empty data for block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_chart_value_error_raises_app_exception() -> None:
    """Verify chart ValueError is translated into AppException with HTTP 500."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [SduiRadarChartBlock(axes=[])])

    with patch("backend_v2.services.pdf_generator.generate_radar_chart", side_effect=ValueError("invalid axis")):
        with pytest.raises(AppException) as exc_info:
            await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="fi")
        assert "Failed to render PDF charts" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_unsupported_locale_raises() -> None:
    """Verify unsupported locale code raises AppException with HTTP 400."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [])

    with pytest.raises(AppException) as exc_info:
        await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="xx_YY")
    assert "is not supported in .arb L10n files" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_localization_load_failure_raises() -> None:
    """Verify localization loader failure raises ConfigurationError."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [])

    with patch("backend_v2.services.pdf_generator.LocalizationService.load_if_needed", side_effect=RuntimeError("io")):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="fi")
        assert "Failed to load localization" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_unknown_block_type_skipped() -> None:
    """Verify non-chart SDUI blocks (ParagraphBlock) skip chart generation cleanly."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_3, [ParagraphBlock(text="Hello", exact_quotes=[], citations=[])])

    pdf_bytes = await svc.generate_execution_pdf(execution_id=_EXEC_ID_3, report_dto=dto, locale="en")
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)


@pytest.mark.asyncio
async def test_pdf_generator_filters_and_matrix_summary() -> None:
    """Verify custom Jinja2 markdown and atom grouping filters and matrix table HTML rendering."""
    svc = PdfReportService()

    md_filter = svc.env.filters["md"]
    assert callable(md_filter)
    assert md_filter(None, "") == ""
    assert md_filter(None, 123) == "<p>123</p>"

    group_filter = svc.env.filters["group_atoms_by_level"]
    assert callable(group_filter)
    assert group_filter([]) == {}
    atom1 = ScorecardAtomDTO(
        atom_id="atm_11111111111111111111111111111111",
        level=1,
        level_name="Level 1",
        claim_label="Claim 1",
        extracted_facts={"fact1": "val1"},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="p1",
            step_2_scan_source="s1",
            step_3_evaluate_anti_patterns="a1",
            step_4_final_conclusion="c1",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="reasoning",
        contextual_override=False,
        structural_location=None,
        chart_display_label="A1",
        visual_intent=VisualIntent.SUCCESS,
    )
    atom2 = ScorecardAtomDTO(
        atom_id="atm_22222222222222222222222222222222",
        level=2,
        level_name="Level 2",
        claim_label="Claim 2",
        extracted_facts={"fact2": "val2"},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="p2",
            step_2_scan_source="s2",
            step_3_evaluate_anti_patterns="a2",
            step_4_final_conclusion="c2",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="reasoning",
        contextual_override=False,
        structural_location=None,
        chart_display_label="A2",
        visual_intent=VisualIntent.SUCCESS,
    )
    grouped = group_filter([atom1, atom2])
    assert 1 in grouped and 2 in grouped

    axis = _make_axis([atom1])
    block = SduiMatrixTableBlock(
        matrix_visible_columns=["label", "distribution", "row_explanation", "normalized_score", "raw_score"],
        axes=[axis],
    )
    meta_block = SduiMetadataBlock(
        title="Testiprofiili",
        badges=[],
        metadata_lines=["Aika: 01.01.2026 12:00"],
    )
    dto = _make_report_dto(
        _EXEC_ID_1,
        [meta_block, block],
        profile_name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
    )
    html = await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale=None)
    assert "Test Axis" in html
    assert "Testiprofiili" in html


@pytest.mark.asyncio
async def test_pdf_generator_renders_multi_segment_quotes() -> None:
    """Positive contract: PDF HTML renders multi-segment quotes joined with ' [...] ' without errors."""
    svc = PdfReportService()
    atom = ScorecardAtomDTO(
        atom_id="atm_11111111111111111111111111111111",
        level=1,
        level_name="Level 1",
        claim_label="Claim 1",
        extracted_facts={"fact1": "val1"},
        exact_quotes=[
            QuoteEvidenceDTO(
                source_quotes=("Part 1", "Part 2"),
                verified_source_ids=["src_0"],
            )
        ],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="p1",
            step_2_scan_source="s1",
            step_3_evaluate_anti_patterns="a1",
            step_4_final_conclusion="c1",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="reasoning",
        contextual_override=False,
        structural_location=None,
        chart_display_label="A1",
        visual_intent=VisualIntent.SUCCESS,
    )
    axis = _make_axis([atom])
    block = SduiMatrixTableBlock(
        matrix_visible_columns=["label", "quotes", "distribution", "row_explanation", "normalized_score"],
        axes=[axis],
    )
    dto = _make_report_dto(
        _EXEC_ID_1,
        [block],
        profile_name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
    )
    html = await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="fi")
    assert "Part 1 [...] Part 2" in html


def test_pdf_generator_raise_unrecognized_sdui_block() -> None:
    """Verify raise_unrecognized_sdui_block global raises AppException with HTTP 500."""
    svc = PdfReportService()
    fn = svc.env.globals["raise_unrecognized_sdui_block"]
    assert callable(fn)
    with pytest.raises(AppException) as exc_info:
        fn("unknown_custom_block")
    assert exc_info.value.status_code == 500
    assert "Unrecognized SDUI block_type 'unknown_custom_block'" in exc_info.value.message


@pytest.mark.asyncio
async def test_pdf_generator_render_html_unexpected_exception() -> None:
    """Verify unexpected runtime error in template retrieval raises AppException with HTTP 500."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [], profile_name=I18nText(translations={"en": "Test Profile"}))
    with patch.object(svc.env, "get_template", side_effect=RuntimeError("disk error")):
        with pytest.raises(AppException) as exc_info:
            await svc.generate_execution_html(execution_id=_EXEC_ID_1, report_dto=dto, locale="en")
        assert exc_info.value.status_code == 500
        assert "HTML generation failed" in exc_info.value.message


@pytest.mark.asyncio
async def test_pdf_generator_render_pdf_empty_weasyprint_output() -> None:
    """Verify empty WeasyPrint write_pdf output returns empty bytes cleanly."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [], profile_name=I18nText(translations={"en": "Test Profile"}))
    mock_html_instance = MagicMock()
    mock_html_instance.write_pdf.return_value = None
    with patch("weasyprint.HTML", return_value=mock_html_instance):
        pdf_bytes = await svc.generate_execution_pdf(execution_id=_EXEC_ID_1, report_dto=dto, locale="en")
        assert pdf_bytes == b""


@pytest.mark.asyncio
async def test_pdf_generator_render_pdf_unexpected_exception() -> None:
    """Verify unexpected WeasyPrint runtime crash raises AppException with HTTP 500."""
    svc = PdfReportService()
    dto = _make_report_dto(_EXEC_ID_1, [], profile_name=I18nText(translations={"en": "Test Profile"}))
    with patch("weasyprint.HTML", side_effect=RuntimeError("weasyprint crash")):
        with pytest.raises(AppException) as exc_info:
            await svc.generate_execution_pdf(execution_id=_EXEC_ID_1, report_dto=dto, locale="en")
        assert exc_info.value.status_code == 500
        assert "PDF generation failed" in exc_info.value.message
