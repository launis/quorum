"""Unit tests for ExportService covering Excel and flat CSV exports."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.atom_result import AtomResultDTO, ErrorDetailsDTO, HydratedAtomDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType
from backend_v2.models.view.sdui import ParagraphBlock, SduiRadarChartBlock
from backend_v2.services.export_service import ExportService, _extract_claim_rule
from backend_v2.tests.fakes.in_memory_repositories import InMemoryComponentRepository


def _build_sample_execution(
    status: ExecutionStatus = ExecutionStatus.PASSED, has_atoms: bool = True
) -> ExecutionRecord:
    step_states: dict[str, ExecutionStepState] = {}
    if has_atoms:
        step_states["stp_0123456789abcdef"] = ExecutionStepState(
            id="stp_0123456789abcdef",
            label="Matrix Step Label",
            status=ExecutionStatus.PASSED,
        )

    return ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=status,
        step_states=step_states,
    )


def _build_sample_report_dto(has_atoms: bool = True) -> ReportDataDTO:
    axis = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.5,
        scale_max=5.0,
        row_explanation="Explanation for row 1",
        is_evaluative=True,
    )
    chart = SduiRadarChartBlock(axes=[axis])
    results: list[AtomResultDTO] = []
    hydrated_references: dict[str, HydratedAtomDTO] = {}
    if has_atoms:
        results = [
            AtomResultDTO(
                tda_id="tda_0123456789abcdef",
                matrix_id="blk_0123456789abcdef",
                status=ExecutionStatus.PASSED,
                source_quote="Verbatim quote from source document",
                evaluation_reasoning="Reasoning with several words here",
            )
        ]
        hydrated_references = {
            "tda_0123456789abcdef": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim Label",
            )
        }
    return ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.5,
        has_warning=False,
        inner_sdui_blocks=[chart],
        results=results,
        hydrated_references=hydrated_references,
    )


def test_extract_claim_rule() -> None:
    lbl = I18nText(translations={"fi": "L", "en": "L"})
    desc = I18nText(translations={"fi": "D", "en": "D"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])

    matrix_block = MatrixPromptBlock(
        id="blk_1111111111111111",
        slug="matrix_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="Matrix rule",
    )
    assert _extract_claim_rule(matrix_block) == "Matrix rule"

    rule_block = SystemRulePromptBlock(
        id="blk_2222222222222222",
        slug="rule_slug",
        label=lbl,
        description=desc,
        instruction_text="Rule text",
    )
    assert _extract_claim_rule(rule_block) == "Rule text"

    persona_block = PersonaPromptBlock(
        id="blk_3333333333333333",
        slug="persona_slug",
        label=lbl,
        description=desc,
        role_enforcement="Persona text",
    )
    assert _extract_claim_rule(persona_block) == "Persona text"

    protocol_block = ProtocolPromptBlock(
        id="blk_4444444444444444",
        slug="proto_slug",
        label=lbl,
        description=desc,
        protocol_instructions="Protocol text",
    )
    assert _extract_claim_rule(protocol_block) == "Protocol text"

    assert _extract_claim_rule(None) == ""


@pytest.mark.asyncio
async def test_export_excel_success_fi() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    lbl = I18nText(translations={"fi": "L", "en": "L"})
    desc = I18nText(translations={"fi": "D", "en": "D"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])
    matrix_block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="m_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="Operational rule",
    )
    bytes_out, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        locale="fi",
        components=[matrix_block],
    )

    assert filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(bytes_out) > 0
    assert bytes_out.startswith(b"PK")


@pytest.mark.asyncio
async def test_export_excel_success_en_with_comp_repo() -> None:
    comp_repo = InMemoryComponentRepository()
    lbl = I18nText(translations={"fi": "L", "en": "L"})
    desc = I18nText(translations={"fi": "D", "en": "D"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])
    matrix_block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="m_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="English operational rule",
    )
    await comp_repo.create_component(matrix_block)

    service = ExportService(comp_repo=comp_repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    bytes_out, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        locale="en",
    )

    assert filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(bytes_out) > 0
    assert comp_repo._call_counts.get("get_all_components", 0) == 1


@pytest.mark.asyncio
async def test_export_excel_fails_non_passed_status() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.FAILED)

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(execution=exec_record, report_dto=None)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Execution must be in PASSED state" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_fails_no_scoreable_atoms() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(execution=exec_record, report_dto=None)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Execution has no scoreable atoms" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_fails_when_report_dto_has_no_atoms() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)
    report_dto = _build_sample_report_dto(has_atoms=False)

    with pytest.raises(AppException) as exc_info:
        await service.export_excel(execution=exec_record, report_dto=report_dto)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Execution has no scoreable atoms" in exc_info.value.message


@pytest.mark.asyncio
async def test_export_excel_writer_error() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    with patch("pandas.ExcelWriter", side_effect=RuntimeError("Disk failure")):
        with pytest.raises(AppException) as exc_info:
            await service.export_excel(execution=exec_record, report_dto=report_dto)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value


def test_export_flat_csv_success() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    csv_bytes, filename = service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        execution_id="exe_custom_999",
    )

    assert filename == "execution_export_exe_custom_999.csv"
    assert len(csv_bytes) > 0
    csv_text = csv_bytes.decode("utf-8")
    assert "execution_id" in csv_text or "status" in csv_text


@pytest.mark.asyncio
async def test_export_excel_with_report_dto_results_atoms() -> None:
    """Regression test proving failure when atoms are passed in report_dto.results.

    During real runtime DAG execution, ExecutionRecord.step_states has empty scorecard_atoms={}.
    The evaluated atoms exist exclusively as AtomResultDTOs inside report_dto.results and
    hydrated_references. ExportService must extract raw data rows from report_dto.results
    instead of failing with 'Execution has no scoreable atoms'.
    """
    from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
    from backend_v2.models.enums import ExecutionStatus

    service = ExportService()
    # Real execution has empty scorecard_atoms in step_states
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)

    atom_result = AtomResultDTO(
        tda_id="tda_0123456789abcdef",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quote="Verbatim quote from source document",
        evaluation_reasoning="Sound reasoning based on evidence.",
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component="boolean_card",
        resolved_claim="The organization follows clear strategy guidelines.",
    )

    axis = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Strategy Matrix",
        label_i18n=I18nText(translations={"fi": "Strategiamatriisi", "en": "Strategy Matrix"}),
        score=4.0,
        scale_max=5.0,
        row_explanation="Solid strategic alignment.",
        is_evaluative=True,
    )
    chart = SduiRadarChartBlock(axes=[axis])

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[chart],
        results=[atom_result],
        hydrated_references={"tda_0123456789abcdef": hydrated_ref},
    )

    excel_bytes, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        locale="fi",
    )

    assert filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert len(excel_bytes) > 0


@pytest.mark.asyncio
async def test_export_excel_with_all_extensions_and_blocks() -> None:
    """Test Excel export with non-matrix blocks, None labels, all atom extensions, and custom ID."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED, has_atoms=False)

    axis_custom = MatrixScorecardRowDTO(
        block_id="blk_aaaaaaaaaaaaaaaa",
        name="Custom Axis",
        label_i18n=I18nText(translations={"en": "Custom Axis"}),
        score=3.0,
        scale_max=5.0,
        row_explanation="Axis with custom label",
        is_evaluative=True,
    )
    chart = SduiRadarChartBlock(axes=[axis_custom])
    text_block = ParagraphBlock(text="Informational text")

    atom_with_extensions = AtomResultDTO(
        tda_id="tda_bbbbbbbbbbbbbbbb",
        matrix_id="blk_aaaaaaaaaaaaaaaa",
        status=ExecutionStatus.FAILED,
        source_quote=None,
        evaluation_reasoning="Failed check due to missing policy.",
        extensions={
            "internalized_rule": "Strict rule",
            "confidence": "0.85",
            "source_id": "src_custom",
            "falsification": "Refuted claim",
        },
    )
    atom_system_error = AtomResultDTO(
        tda_id="tda_cccccccccccccccc",
        matrix_id="blk_aaaaaaaaaaaaaaaa",
        status=ExecutionStatus.SYSTEM_ERROR,
        source_quote=None,
        evaluation_reasoning=None,
        error_details=ErrorDetailsDTO(error_code="SYSTEM_ERROR", message="System execution failure."),
    )
    hydrated_ref_with_quote = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Resolved Claim with Quote",
        source_quote="Quote from hydrated reference",
    )

    component_block = SystemRulePromptBlock(
        id="blk_dddddddddddddddd",
        slug="comp_slug",
        label=I18nText(translations={"fi": "Komponentti", "en": "Component"}),
        description=I18nText(translations={"fi": "D", "en": "D"}),
        instruction_text="Component rule instruction",
    )
    tda_matched_block = SystemRulePromptBlock(
        id="tda_eeeeeeeeeeeeeeee",
        slug="tda_slug",
        label=I18nText(translations={"fi": "TDA Block", "en": "TDA Block"}),
        description=I18nText(translations={"fi": "D", "en": "D"}),
        instruction_text="TDA matched instruction",
    )

    atom_with_comp_matrix = AtomResultDTO(
        tda_id="tda_eeeeeeeeeeeeeeee",
        matrix_id="blk_dddddddddddddddd",
        status=ExecutionStatus.PASSED,
        source_quote="Explicit quote",
        evaluation_reasoning="Evaluation passed smoothly.",
    )
    atom_unmatched = AtomResultDTO(
        tda_id="tda_ffffffffffffffff",
        matrix_id="blk_0000000000000000",
        status=ExecutionStatus.PASSED,
        source_quote="Unknown quote",
        evaluation_reasoning="Evaluation for unknown block.",
    )

    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=3.5,
        has_warning=False,
        inner_sdui_blocks=[text_block, chart],
        results=[atom_with_extensions, atom_system_error, atom_with_comp_matrix, atom_unmatched],
        hydrated_references={
            "tda_bbbbbbbbbbbbbbbb": hydrated_ref_with_quote,
            "tda_cccccccccccccccc": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for system error",
            ),
            "tda_eeeeeeeeeeeeeeee": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for component matrix",
            ),
            "tda_ffffffffffffffff": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Claim for unknown block",
            ),
        },
    )

    excel_bytes, filename = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        locale="en",
        components=[component_block, tda_matched_block],
        execution_id="exe_custom_export_123",
    )

    assert filename == "execution_export_exe_custom_export_123.xlsx"
    assert len(excel_bytes) > 0


def test_export_flat_csv_default_execution_id() -> None:
    """Test flat CSV export without explicit execution_id."""
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    csv_bytes, filename = service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
    )

    assert filename == "execution_export_exe_0123456789abcdef.csv"
    assert len(csv_bytes) > 0
