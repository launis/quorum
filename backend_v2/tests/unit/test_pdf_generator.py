"""Unit tests for PdfReportService Dumb Painter."""

from unittest.mock import patch

import pytest

from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.enums import VisualIntent
from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO, ReportDataDTO, ScorecardAtomDTO
from backend_v2.models.view.sdui import (
    ParagraphBlock,
    SduiMatrixTableBlock,
    SduiMetadataBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.pdf_generator import PdfReportService


@pytest.mark.asyncio
async def test_pdf_generator_chart_injection_failure_safe() -> None:
    svc = PdfReportService()

    # Empty layout (should not invoke chart rendering)
    dto = ReportDataDTO(
        execution_id="exe_aaaaaaaabbbbbbbb",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiMetrics1DBlock(axes=[])],
    )

    pdf_bytes = await svc.generate_execution_pdf(execution_id="exe_aaaaaaaabbbbbbbb", report_dto=dto, locale="en")
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)


@pytest.mark.asyncio
async def test_html_generator_chart_injection_failure_safe() -> None:
    svc = PdfReportService()

    # Empty layout (should not invoke chart rendering)
    dto = ReportDataDTO(
        execution_id="exe_aaaaaaaabbbbbbbb",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiMetrics1DBlock(axes=[])],
    )

    html_string = await svc.generate_execution_html(execution_id="exe_aaaaaaaabbbbbbbb", report_dto=dto, locale="en")
    assert html_string is not None
    assert isinstance(html_string, str)
    assert html_string.strip().startswith("<!DOCTYPE html>")


@pytest.mark.asyncio
async def test_pdf_generator_empty_radar_chart_crashes() -> None:
    svc = PdfReportService()

    dto = ReportDataDTO(
        execution_id="exe_1111111111111111",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiRadarChartBlock(axes=[])],
    )

    with patch("backend_v2.services.pdf_generator.generate_radar_chart", return_value=""):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_pdf(execution_id="exe_1111111111111111", report_dto=dto, locale="en")
        assert "returned empty data for block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_scatter_plot_rendering() -> None:
    svc = PdfReportService()

    dto = ReportDataDTO(
        execution_id="exe_scatter11111111",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiScatterPlotBlock(axes=[])],
    )

    with patch("backend_v2.services.pdf_generator.generate_scatter_chart", return_value="fake_b64"):
        html = await svc.generate_execution_html(execution_id="exe_scatter11111111", report_dto=dto, locale="fi")
        assert "fake_b64" in html


@pytest.mark.asyncio
async def test_pdf_generator_empty_scatter_plot_crashes() -> None:
    svc = PdfReportService()

    dto = ReportDataDTO(
        execution_id="exe_scatter22222222",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiScatterPlotBlock(axes=[])],
    )

    with patch("backend_v2.services.pdf_generator.generate_scatter_chart", return_value=""):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_pdf(execution_id="exe_scatter22222222", report_dto=dto, locale="fi")
        assert "generate_scatter_chart returned empty data for block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_chart_value_error_raises_app_exception() -> None:
    svc = PdfReportService()

    dto = ReportDataDTO(
        execution_id="exe_err111111111111",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiRadarChartBlock(axes=[])],
    )

    with patch("backend_v2.services.pdf_generator.generate_radar_chart", side_effect=ValueError("invalid axis")):
        with pytest.raises(AppException) as exc_info:
            await svc.generate_execution_html(execution_id="exe_err111111111111", report_dto=dto, locale="fi")
        assert "Failed to render PDF charts" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_unsupported_locale_raises() -> None:
    svc = PdfReportService()

    dto = ReportDataDTO(
        execution_id="exe_loc111111111111",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[],
    )

    with pytest.raises(AppException) as exc_info:
        await svc.generate_execution_html(execution_id="exe_loc111111111111", report_dto=dto, locale="xx_YY")
    assert "is not supported in .arb L10n files" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_localization_load_failure_raises() -> None:
    svc = PdfReportService()

    dto = ReportDataDTO(
        execution_id="exe_loc222222222222",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[],
    )

    with patch("backend_v2.services.localization.LocalizationService.load_if_needed", side_effect=RuntimeError("disk")):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_html(execution_id="exe_loc222222222222", report_dto=dto, locale="fi")
        assert "Failed to load localization" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_unknown_block_type_skipped() -> None:
    svc = PdfReportService()

    dto = ReportDataDTO(
        execution_id="exe_2222222222222222",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[ParagraphBlock(text="Hello", exact_quotes=[], citations=[])],
    )

    pdf_bytes = await svc.generate_execution_pdf(execution_id="exe_2222222222222222", report_dto=dto, locale="en")
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)


@pytest.mark.asyncio
async def test_pdf_generator_filters_and_matrix_summary() -> None:
    svc = PdfReportService()

    md_filter = svc.env.filters["md"]
    assert md_filter(None, "") == ""
    assert md_filter(None, 123) == "<p>123</p>"

    group_filter = svc.env.filters["group_atoms_by_level"]
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
        status="PASSED",
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
        status="PASSED",
        semantic_reasoning="reasoning",
        contextual_override=False,
        structural_location=None,
        chart_display_label="A2",
        visual_intent=VisualIntent.SUCCESS,
    )
    grouped = group_filter([atom1, atom2])
    assert 1 in grouped and 2 in grouped

    # Render matrix summary with quotes and level groupings
    axis = MatrixScorecardRowDTO(
        block_id="axis_1",
        name="Test Axis",
        label_i18n=I18nText(default_locale="en", translations={"en": "Test Axis", "fi": "Testi Akseli"}),
        is_evaluative=True,
        allow_contextual_override=True,
        level_names={"1": "Level 1"},
        level_breakdown={"1": "1/1"},
        evaluated_atoms=[atom1],
        row_explanation="All good",
        ui_plot_ratio=0.85,
        score_display_label="85%",
    )
    block = SduiMatrixTableBlock(
        matrix_visible_columns=["label", "distribution", "row_explanation", "quotes", "normalized_score", "score"],
        axes=[axis],
    )
    meta_block = SduiMetadataBlock(
        title="Testiprofiili",
        badges=[],
        metadata_lines=["Aika: 01.01.2026 12:00"],
    )
    dto = ReportDataDTO(
        execution_id="exe_matrix33333333",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        inner_sdui_blocks=[meta_block, block],
    )
    html = await svc.generate_execution_html(execution_id="exe_matrix33333333", report_dto=dto, locale="fi")
    assert "Test Axis" in html
    assert "Testiprofiili" in html
