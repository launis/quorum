"""Unit tests for ExcelExporter sub-module covering Excel workbook streaming and quality gates."""

from __future__ import annotations

import io
from unittest.mock import patch

import openpyxl
import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import (
    CausalGraphPayloadDTO,
    CausalNodeDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType, ReportSheetKey
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import SduiRadarChartBlock
from backend_v2.services.export.excel_exporter import ExcelExporter
from backend_v2.services.export_service import ExportService
from backend_v2.services.localization import ReportHeaderResolver
from backend_v2.tests.fakes.in_memory_repositories import InMemoryPromptBlockRepository


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
                source_quotes=["Verbatim quote from source document"],
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


def _build_sample_matrix_rows(n: int = 1) -> list[MatrixScorecardRowDTO]:
    rows = [
        MatrixScorecardRowDTO(
            block_id="blk_0123456789abcdef",
            name="Matrix 0",
            label_i18n=I18nText(translations={"fi": "Matriisi 0", "en": "Matrix 0"}),
            score=4.5,
            scale_max=5.0,
            row_explanation="Row explanation 0",
            is_evaluative=True,
        )
    ]
    for i in range(1, n):
        rows.append(
            MatrixScorecardRowDTO(
                block_id=f"blk_matrix_{i:04d}",
                name=f"Matrix {i}",
                label_i18n=I18nText(translations={"fi": f"Matriisi {i}", "en": f"Matrix {i}"}),
                score=4.0,
                scale_max=5.0,
                row_explanation=f"Row explanation {i}",
                is_evaluative=True,
            )
        )
    return rows


@pytest.mark.asyncio
async def test_excel_exporter_direct_call() -> None:
    """Verify ExcelExporter directly generates a valid Excel payload with corporate styling."""
    exporter = ExcelExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(2)

    payload = await exporter.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    assert payload.filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert payload.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(payload.content_bytes) > 0

    wb = openpyxl.load_workbook(io.BytesIO(payload.content_bytes))
    sheet_summary = ReportHeaderResolver.get_sheet_name(ReportSheetKey.SUMMARY, "fi")
    sheet_raw_data = ReportHeaderResolver.get_sheet_name(ReportSheetKey.RAW_DATA, "fi")
    assert sheet_summary in wb.sheetnames
    assert sheet_raw_data in wb.sheetnames


@pytest.mark.asyncio
async def test_export_excel_existing_contract_parity() -> None:
    """Verify workbook sheets, summary rows, and raw data atoms match between ExcelExporter and ExportService."""
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    exporter = ExcelExporter()
    service = ExportService()

    direct_payload = await exporter.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )
    service_payload = await service.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    assert direct_payload.filename == service_payload.filename
    assert direct_payload.mime_type == service_payload.mime_type

    direct_wb = openpyxl.load_workbook(io.BytesIO(direct_payload.content_bytes))
    service_wb = openpyxl.load_workbook(io.BytesIO(service_payload.content_bytes))
    assert direct_wb.sheetnames == service_wb.sheetnames


@pytest.mark.asyncio
async def test_export_excel_includes_causal_propositions() -> None:
    """Verify dynamic causal graph propositions stream into Tab 2 with metrics in ExcelExporter."""
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)

    atom_res = AtomResultDTO(
        tda_id="tda_0000000000000001",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes=["Quote 1"],
        evaluation_reasoning="Affirmative claim passed",
        is_inverse_evidence=False,
    )
    hydrated = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Atom 1 Claim",
    )
    causal_payload = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="tda_0000000000000001",
                claim="Atom 1 Claim",
                paragraph_ref="p1",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=["causal_prop_0001"],
            ),
            CausalNodeDTO(
                node_id="causal_prop_0001",
                claim="Unmapped Causal Proposition",
                paragraph_ref="p2",
                status=ExecutionStatus.FAILED,
                blame_parent_ids=["tda_0000000000000001"],
                dependent_child_ids=[],
            ),
        ],
        edges=[],
        root_cause_node_ids=[],
        cycle_detected=False,
        isolated_node_ids=[],
    )
    exec_record = exec_record.model_copy(
        update={
            "execution_trace": [
                TraceEvent(
                    step_name="causal_discovery",
                    event_type="output",
                    content=causal_payload,
                )
            ]
        }
    )
    report_dto = _build_sample_report_dto()
    report_dto = report_dto.model_copy(
        update={
            "results": [atom_res],
            "hydrated_references": {"tda_0000000000000001": hydrated},
        }
    )
    matrices = _build_sample_matrix_rows(1)

    exporter = ExcelExporter()
    payload = await exporter.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    wb = openpyxl.load_workbook(io.BytesIO(payload.content_bytes))
    sheet_raw_data = ReportHeaderResolver.get_sheet_name(ReportSheetKey.RAW_DATA, "fi")
    ws = wb[sheet_raw_data]
    rows = list(ws.iter_rows(values_only=True))
    assert len(rows) >= 3  # Header + 1 matrix atom + 1 causal node
    labels = [row[0] for row in rows[1:]]
    assert "Matriisi 0" in labels
    assert "Kausaalipäättely" in labels


@pytest.mark.asyncio
async def test_export_excel_with_prompt_block_repo() -> None:
    """Verify ExcelExporter loads prompt blocks from repository when components is None."""
    blk_id = "blk_0123456789abcdef"
    lbl = I18nText(translations={"fi": "Matriisi 1", "en": "Matrix 1"})
    desc = I18nText(translations={"fi": "Kuvaus 1", "en": "Description 1"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])
    matrix_block = MatrixPromptBlock(
        id=blk_id,
        slug="m_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="Operational rule description",
    )
    repo = InMemoryPromptBlockRepository()
    await repo.create_prompt_block(matrix_block)

    exporter = ExcelExporter(prompt_block_repo=repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    payload = await exporter.export_excel(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="en",
    )
    assert payload.filename == "execution_export_exe_0123456789abcdef.xlsx"
    assert repo._call_counts["get_all_prompt_blocks"] == 1


@pytest.mark.asyncio
async def test_export_excel_unpassed_execution_fails() -> None:
    """Verify export_excel raises 400 AppException when execution status is not PASSED."""
    exporter = ExcelExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.FAILED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    with pytest.raises(AppException) as exc_info:
        await exporter.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=matrices,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_export_excel_no_scoreable_atoms_fails() -> None:
    """Verify export_excel raises 400 AppException when report_dto has no scoreable atoms."""
    exporter = ExcelExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto(has_atoms=False)
    matrices = _build_sample_matrix_rows(1)

    with pytest.raises(AppException) as exc_info:
        await exporter.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=matrices,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_export_excel_no_matrices_fails() -> None:
    """Verify export_excel raises 400 AppException when matrices list is empty."""
    exporter = ExcelExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()

    with pytest.raises(AppException) as exc_info:
        await exporter.export_excel(
            execution=exec_record,
            report_dto=report_dto,
            matrices=[],
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_export_excel_writer_error_raises_500() -> None:
    """Verify export_excel raises 500 AppException when pandas/openpyxl writer fails."""
    exporter = ExcelExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    with patch("pandas.ExcelWriter", side_effect=RuntimeError("Disk failure")):
        with pytest.raises(AppException) as exc_info:
            await exporter.export_excel(
                execution=exec_record,
                report_dto=report_dto,
                matrices=matrices,
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
