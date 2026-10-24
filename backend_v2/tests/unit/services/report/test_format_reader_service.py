"""Unit test suite for ReportFormatReaderService verifying storage retrieval, byte streaming, and tabular row projection."""

import logging
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.report_artifact import (
    ReportMetadataDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    LaxSDUIComponentType,
    ReportStatus,
)
from backend_v2.services.report.format_reader_service import ReportFormatReaderService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_dummy_report(
    report_id: str = "rep_1234567890abcdef",
    status: ReportStatus = ReportStatus.READY,
) -> ReportArtifact:
    now = datetime.now(UTC)
    return ReportArtifact(
        id=report_id,
        execution_id="exe_1234567890abcdef",
        workflow_id="wor_0123456789abcdef",
        profile_id="prf_1234567890abcdef",
        locale="fi",
        title="Johdon raportti",
        status=status,
        storage_paths=ReportStoragePathsDTO(
            pdf_path=f"artifacts/reports/{report_id}/report.pdf",
            sdui_json_path=f"artifacts/reports/{report_id}/report.sdui.json",
            excel_path=f"artifacts/reports/{report_id}/report.xlsx",
            csv_path=f"artifacts/reports/{report_id}/report.csv",
        ),
        metadata=ReportMetadataDTO(cost_usd=0.05, duration_ms=1200, tokens_used=500),
        created_at=now,
        updated_at=now,
    )


def _create_dummy_report_data_dto() -> ReportDataDTO:
    atom_passed = AtomResultDTO(
        tda_id="tda_0123456789abcdef",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes=("Forensic quote 1", "Forensic quote 2"),
        evaluation_reasoning="Sound reasoning.",
        is_inverse_evidence=False,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_failed_unhydrated = AtomResultDTO(
        tda_id="tda_0000000000000002",
        matrix_id=None,
        status=ExecutionStatus.FAILED,
        source_quotes=None,
        evaluation_reasoning="Missing evidence.",
        is_inverse_evidence=False,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_passed_inverse = AtomResultDTO(
        tda_id="tda_0000000000000003",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes=None,
        evaluation_reasoning="Inverse passed.",
        is_inverse_evidence=True,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Strategic Claim",
    )
    return ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_passed, atom_failed_unhydrated, atom_passed_inverse],
        hydrated_references={
            "tda_0123456789abcdef": hydrated_ref,
            "tda_0000000000000002": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Failed Claim",
            ),
            "tda_0000000000000003": HydratedAtomDTO(
                sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Inverse Claim",
            ),
        },
    )


@pytest.mark.asyncio
async def test_get_report_sdui_success() -> None:
    """Verify get_report_sdui hydrates and returns ReportDataDTO fail-fast for an existing READY report."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    expected_dto = _create_dummy_report_data_dto()
    storage = AsyncMock()
    storage.read.return_value = expected_dto.model_dump_json().encode("utf-8")

    service = ReportFormatReaderService(repo=repo, storage_driver=storage)
    result = await service.get_report_sdui(report.id)

    assert isinstance(result, ReportDataDTO)
    assert result.execution_id == expected_dto.execution_id
    assert result.profile_id == expected_dto.profile_id
    assert result.global_score == 4.0
    storage.read.assert_awaited_once_with(f"artifacts/reports/{report.id}/report.sdui.json")


@pytest.mark.asyncio
async def test_get_report_pdf_bytes_success() -> None:
    """Verify get_report_pdf_bytes returns raw PDF bytes and deterministic filename for a READY report."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    storage = AsyncMock()
    storage.read.return_value = b"%PDF-1.7 sample pdf payload"

    service = ReportFormatReaderService(repo=repo, storage_driver=storage)
    pdf_bytes, filename = await service.get_report_pdf_bytes(report.id)

    assert pdf_bytes == b"%PDF-1.7 sample pdf payload"
    assert filename == f"report_{report.id}.pdf"
    storage.read.assert_awaited_once_with(f"artifacts/reports/{report.id}/report.pdf")


@pytest.mark.asyncio
async def test_get_report_excel_and_csv_bytes_success() -> None:
    """Verify get_report_excel_bytes and get_report_csv_bytes stream stored bytes and filenames."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    storage = AsyncMock()
    storage.read.side_effect = [b"excel_binary_content", b"csv_flat_content"]

    service = ReportFormatReaderService(repo=repo, storage_driver=storage)
    excel_bytes, excel_name = await service.get_report_excel_bytes(report.id)
    assert excel_bytes == b"excel_binary_content"
    assert excel_name == f"report_{report.id}.xlsx"

    csv_bytes, csv_name = await service.get_report_csv_bytes(report.id)
    assert csv_bytes == b"csv_flat_content"
    assert csv_name == f"report_{report.id}.csv"


@pytest.mark.asyncio
async def test_get_report_rows_and_dlq_log(caplog: pytest.LogCaptureFixture) -> None:
    """Verify get_report_rows projects evaluated rows across passed/failed/hydrated/unhydrated atoms."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    storage = AsyncMock()
    storage.read.return_value = _create_dummy_report_data_dto().model_dump_json().encode("utf-8")

    service = ReportFormatReaderService(repo=repo, storage_driver=storage)
    rows = await service.get_report_rows(report.id)

    assert len(rows) == 3
    assert rows[0].metric_key == "blk_0123456789abcdef"
    assert rows[0].metric_label == "Strategic Claim"
    assert rows[0].score == 1.0
    assert rows[0].quote == "Forensic quote 1 [...] Forensic quote 2"
    assert rows[0].is_inverse_evidence is False

    assert rows[1].metric_key == "tda_0000000000000002"
    assert rows[1].metric_label == "Failed Claim"
    assert rows[1].score == 0.0
    assert rows[1].quote is None
    assert rows[1].is_inverse_evidence is False

    assert rows[2].metric_key == "blk_0123456789abcdef"
    assert rows[2].metric_label == "Inverse Claim"
    assert rows[2].score == 1.0
    assert rows[2].quote is None
    assert rows[2].is_inverse_evidence is True

    with caplog.at_level(logging.DEBUG):
        service._dlq_log_absent_storage_artifact("artifacts/reports/rep_1/missing.pdf")
    assert "already absent during deletion" in caplog.text


@pytest.mark.asyncio
async def test_format_reader_negative_not_found_and_not_ready() -> None:
    """Verify negative cases: missing report raises ResourceNotFoundError and non-READY status raises 409."""
    repo = InMemoryUnifiedWorkflowRepository()
    storage = AsyncMock()
    service = ReportFormatReaderService(repo=repo, storage_driver=storage)

    # 1. Missing report_id raises ResourceNotFoundError
    with pytest.raises(ResourceNotFoundError) as exc_not_found:
        await service.get_report_sdui("rep_0000000000000000")
    assert exc_not_found.value.details is not None
    assert exc_not_found.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    # 2. Report in PENDING status raises AppException 409 REPORT_NOT_READY
    pending_report = _create_dummy_report(report_id="rep_0000000000000001", status=ReportStatus.PENDING)
    await repo.create_report_artifact(pending_report)
    with pytest.raises(AppException) as exc_not_ready:
        await service.get_report_pdf_bytes(pending_report.id)
    assert exc_not_ready.value.status_code == 409
    assert exc_not_ready.value.details is not None
    assert exc_not_ready.value.details["error_code"] == ErrorCodes.REPORT_NOT_READY.value

    # 3. Report with empty storage path raises AppException 409 REPORT_NOT_READY
    empty_path_report = _create_dummy_report(report_id="rep_0000000000000002", status=ReportStatus.READY).model_copy(
        update={"storage_paths": ReportStoragePathsDTO(pdf_path=None)}
    )
    await repo.create_report_artifact(empty_path_report)
    with pytest.raises(AppException) as exc_no_path:
        await service.get_report_pdf_bytes(empty_path_report.id)
    assert exc_no_path.value.status_code == 409


@pytest.mark.asyncio
async def test_format_reader_negative_storage_read_failure() -> None:
    """Verify storage driver OSError/ValueError raises AppException 500 STORAGE_ACCESS_FAILED."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    storage = AsyncMock()
    storage.read.side_effect = OSError("Disk read failure")

    service = ReportFormatReaderService(repo=repo, storage_driver=storage)
    with pytest.raises(AppException) as exc_storage:
        await service.get_report_pdf_bytes(report.id)

    assert exc_storage.value.status_code == 500
    assert exc_storage.value.details is not None
    assert exc_storage.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
