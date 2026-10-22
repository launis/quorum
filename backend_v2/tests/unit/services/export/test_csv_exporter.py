"""Unit tests for CsvExporter sub-module covering 22-column flat CSV streaming and quality gates."""

from __future__ import annotations

import csv
import io

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
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import SduiRadarChartBlock
from backend_v2.services.export import ExportService
from backend_v2.services.export.csv_exporter import CsvExporter
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
async def test_csv_exporter_direct_call() -> None:
    """Verify CsvExporter directly generates a valid 22-column flat CSV payload with utf-8-sig."""
    exporter = CsvExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    assert payload.filename == "execution_export_exe_0123456789abcdef.csv"
    assert payload.mime_type == "text/csv"
    assert len(payload.content_bytes) > 0

    decoded = payload.content_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(decoded))
    header = next(reader)
    expected_headers = ReportHeaderResolver.get_all_denormalized_csv_headers("fi")
    assert header == expected_headers
    assert len(header) == 22


@pytest.mark.asyncio
async def test_export_flat_csv_existing_contract_parity() -> None:
    """Verify 22-column CSV stream matches byte content between CsvExporter and ExportService."""
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    exporter = CsvExporter()
    service = ExportService()

    direct_payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )
    service_payload = await service.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )

    assert direct_payload.filename == service_payload.filename
    assert direct_payload.mime_type == service_payload.mime_type
    assert direct_payload.content_bytes == service_payload.content_bytes


@pytest.mark.asyncio
async def test_export_csv_includes_causal_and_ml_columns() -> None:
    """Verify CSV flat stream includes dynamic causal graph metadata and ML indicators."""
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)

    atom_res_1 = AtomResultDTO(
        tda_id="tda_0000000000000001",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes="Quote 1",
        evaluation_reasoning="Affirmative passed",
        is_inverse_evidence=False,
    )
    hydrated_1 = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Criterion 1",
    )
    atom_res_2 = AtomResultDTO(
        tda_id="tda_0000000000000002",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes=None,
        evaluation_reasoning="Inverse claim passed (anti-pattern absent = clean finding)",
        is_inverse_evidence=True,
    )
    hydrated_2 = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Anti-pattern 1",
    )

    causal_payload_csv = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="causal_prop_0002",
                claim="Standalone Causal Node",
                paragraph_ref="p3",
                status=ExecutionStatus.SYSTEM_ERROR,
                blame_parent_ids=[],
                dependent_child_ids=[],
            ),
        ],
        edges=[],
        root_cause_node_ids=["causal_prop_0002"],
        cycle_detected=False,
        isolated_node_ids=[],
    )
    exec_record = exec_record.model_copy(
        update={
            "execution_trace": [
                TraceEvent(
                    step_name="causal_discovery",
                    event_type="output",
                    content=causal_payload_csv,
                )
            ]
        }
    )
    report_dto = _build_sample_report_dto()
    report_dto = report_dto.model_copy(
        update={
            "results": [atom_res_1, atom_res_2],
            "hydrated_references": {
                "tda_0000000000000001": hydrated_1,
                "tda_0000000000000002": hydrated_2,
            },
        }
    )

    exporter = CsvExporter()
    payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=_build_sample_matrix_rows(1),
        locale="fi",
    )

    decoded = payload.content_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(decoded))
    next(reader)
    rows = list(reader)
    assert len(rows) == 3  # 2 matrix atoms + 1 unmapped causal node

    # Check is_inverse column (index 14) and points_awarded (index 15)
    row_1 = rows[0]
    assert row_1[14] == "0"  # affirmative
    assert row_1[15] == "1.0"  # 1.0 points for affirmative passed

    row_2 = rows[1]
    assert row_2[14] == "1"  # inverse
    assert row_2[15] == "0.0"  # 0.0 points for inverse passed

    causal_row = rows[2]
    assert causal_row[1] == "Kausaalipäättely"
    assert causal_row[16] == "0"  # result_status 0 for non-PASSED
    assert causal_row[19] == "root_cause"  # causal_status


@pytest.mark.asyncio
async def test_export_flat_csv_with_prompt_block_repo() -> None:
    """Verify CsvExporter resolves blocks from repository when components is None."""
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

    exporter = CsvExporter(prompt_block_repo=repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
    )
    assert payload.filename == "execution_export_exe_0123456789abcdef.csv"
    assert repo._call_counts["get_all_prompt_blocks"] == 1


@pytest.mark.asyncio
async def test_export_flat_csv_unpassed_execution_fails() -> None:
    """Verify export_flat_csv raises 400 AppException when execution status is not PASSED."""
    exporter = CsvExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.FAILED)
    report_dto = _build_sample_report_dto()

    with pytest.raises(AppException) as exc_info:
        await exporter.export_flat_csv(
            execution=exec_record,
            report_dto=report_dto,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_export_flat_csv_no_scoreable_atoms_fails() -> None:
    """Verify export_flat_csv raises 400 AppException when report_dto is None."""
    exporter = CsvExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)

    with pytest.raises(AppException) as exc_info:
        await exporter.export_flat_csv(
            execution=exec_record,
            report_dto=None,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_export_flat_csv_empty_results_fails() -> None:
    """Verify export_flat_csv raises 400 AppException when report_dto results is empty."""
    exporter = CsvExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto(has_atoms=False)

    with pytest.raises(AppException) as exc_info:
        await exporter.export_flat_csv(
            execution=exec_record,
            report_dto=report_dto,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_export_flat_csv_all_matrices_override() -> None:
    """Verify all_matrices parameter overrides matrices parameter in CSV export."""
    exporter = CsvExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    single_matrix = _build_sample_matrix_rows(1)
    two_matrices = _build_sample_matrix_rows(2)

    payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=single_matrix,
        all_matrices=two_matrices,
        locale="fi",
    )

    decoded = payload.content_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(decoded))
    next(reader)
    rows = list(reader)
    assert len(rows) >= 1
    # Check matrix_label column resolves from effective_matrices
    assert rows[0][1] == "Matriisi 0"


@pytest.mark.asyncio
async def test_export_flat_csv_custom_execution_id() -> None:
    """Verify explicit execution_id parameter overrides execution.id in filename and CSV rows."""
    exporter = CsvExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        execution_id="custom_override_id",
        locale="fi",
    )

    assert payload.filename == "execution_export_custom_override_id.csv"
    decoded = payload.content_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(decoded))
    next(reader)
    row = next(reader)
    assert row[0] == "custom_override_id"


@pytest.mark.asyncio
async def test_export_flat_csv_locale_en_resolution() -> None:
    """Verify locale='en' produces English CSV headers and English matrix labels."""
    exporter = CsvExporter()
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        locale="en",
    )

    decoded = payload.content_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(decoded))
    header = next(reader)
    expected_en_headers = ReportHeaderResolver.get_all_denormalized_csv_headers("en")
    assert header == expected_en_headers
    row = next(reader)
    assert row[1] == "Matrix 0"


@pytest.mark.asyncio
async def test_export_flat_csv_with_explicit_components() -> None:
    """Verify explicit components list is used directly without repository queries."""
    blk_id = "blk_0123456789abcdef"
    lbl = I18nText(translations={"fi": "Matriisi Eksplisiittinen", "en": "Matrix Explicit"})
    desc = I18nText(translations={"fi": "Kuvaus", "en": "Description"})
    scale = MatrixScale(score=1, ai_label="L1", claims=[])
    matrix_block = MatrixPromptBlock(
        id=blk_id,
        slug="m_explicit_slug",
        label=lbl,
        description=desc,
        scales=[scale],
        ai_description="Explicit rule description",
    )

    repo = InMemoryPromptBlockRepository()
    exporter = CsvExporter(prompt_block_repo=repo)
    exec_record = _build_sample_execution(status=ExecutionStatus.PASSED)
    report_dto = _build_sample_report_dto()
    matrices = _build_sample_matrix_rows(1)

    payload = await exporter.export_flat_csv(
        execution=exec_record,
        report_dto=report_dto,
        matrices=matrices,
        components=[matrix_block],
        locale="fi",
    )

    assert payload.filename == "execution_export_exe_0123456789abcdef.csv"
    # Repo should NOT have been queried because components was provided
    assert repo.get_call_count("get_all_prompt_blocks") == 0

