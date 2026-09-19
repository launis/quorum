"""Unit tests for ExportService covering Excel and flat CSV exports."""

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.interfaces import IComponentRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.view.sdui import SduiRadarChartBlock
from backend_v2.services.export_service import ExportService, _extract_claim_rule


def _build_sample_execution(status: ExecutionStatus = ExecutionStatus.PASSED, has_atoms: bool = True) -> ExecutionRecord:
    step_states: dict[str, ExecutionStepState] = {}
    if has_atoms:
        atom = ScorecardAtomDTO(
            atom_id="blk_0123456789abcdef",
            level=1,
            level_name="T1",
            claim_label="Claim Label",
            extracted_facts={},
            exact_quotes=[],
            internal_logic_en=ReasoningStepDTO(
                step_1_identify_premise="Premise text",
                step_2_scan_source="Scan text",
                step_3_evaluate_anti_patterns="Falsification text",
                step_4_final_conclusion="Conclusion text",
            ),
            status=ExecutionStatus.PASSED,
            semantic_reasoning="Reasoning with several words here",
            contextual_override=False,
            structural_location=None,
            chart_display_label="Chart Label",
            visual_intent=VisualIntent.NEUTRAL,
        )
        step_states["stp_0123456789abcdef"] = ExecutionStepState(
            id="stp_0123456789abcdef",
            label="Matrix Step Label",
            status=ExecutionStatus.PASSED,
            scorecard_atoms={"blk_0123456789abcdef": atom},
        )

    return ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=status,
        step_states=step_states,
    )


def _build_sample_report_dto() -> ReportDataDTO:
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
    return ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prof_0123456789abcdef",
        global_score=4.5,
        has_warning=False,
        inner_sdui_blocks=[chart],
        results=[],
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
    comp_repo = AsyncMock(spec=IComponentRepository)
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
    comp_repo.get_all_components.return_value = [matrix_block]

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
    comp_repo.get_all_components.assert_awaited_once_with("prompt_block")


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
async def test_export_excel_writer_error() -> None:
    service = ExportService()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)

    with patch("pandas.ExcelWriter", side_effect=RuntimeError("Disk failure")):
        with pytest.raises(AppException) as exc_info:
            await service.export_excel(execution=exec_record, report_dto=None)

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
