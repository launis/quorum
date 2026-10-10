"""Regression test for ReportService synthesis argument order bug.

Validates that generate_profile_synthesis_and_pdf_task is invoked with:
- execution_id: report.execution_id
- accept_language: report.locale
- profile_id: report.profile_id
and NOT with profile_id and locale swapped.
"""

from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.export import ExportPayloadDTO
from backend_v2.models.dtos.report_artifact import ReportMetadataDTO, ReportStoragePathsDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, ReportStatus
from backend_v2.services.report_service import ReportService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers.synthesis_worker import generate_profile_synthesis_and_pdf_task


@pytest.mark.asyncio
async def test_process_artifact_compilation_calls_synthesis_with_correct_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify synthesis worker is invoked with correct parameter bindings (no argument swap)."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = ReportArtifact(
        id="rep_1234567890abcdef",
        execution_id="exe_1234567890abcdef",
        workflow_id="wor_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
        locale="fi",
        title="Test Report",
        status=ReportStatus.PENDING,
        storage_paths=ReportStoragePathsDTO(),
        metadata=ReportMetadataDTO(cost_usd=0.01, duration_ms=100, tokens_used=10),
    )
    execution = ExecutionRecord(
        id=report.execution_id,
        workflow_id=report.workflow_id,
        target_locale=report.locale,
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        step_states={},
        profile_syntheses={},  # profile_id not in profile_syntheses
    )

    await repo.create_report_artifact(report)
    await repo.save_execution(execution)

    mock_synthesis_task = AsyncMock()

    storage = AsyncMock()
    storage.save.side_effect = lambda path, data: path

    export_service = AsyncMock()
    export_service.export_excel.return_value = ExportPayloadDTO(
        content_bytes=b"excel_bytes",
        filename="report.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    export_service.export_flat_csv.return_value = ExportPayloadDTO(
        content_bytes=b"csv_bytes",
        filename="report.csv",
        mime_type="text/csv",
    )

    pdf_service = AsyncMock()
    pdf_service.generate_execution_pdf.return_value = b"pdf_bytes"

    dummy_dto = ReportDataDTO(
        workflow_id=report.workflow_id,
        execution_id=report.execution_id,
        profile_id=report.profile_id,
    )
    from backend_v2.services import blueprint

    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    service = ReportService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
        synthesis_runner=mock_synthesis_task,
    )
    await service.process_artifact_compilation(report.id)

    # Verify that generate_profile_synthesis_and_pdf_task was called with:
    # execution_id=report.execution_id, accept_language=report.locale, profile_id=report.profile_id
    mock_synthesis_task.assert_awaited_once()
    call_args = mock_synthesis_task.await_args
    pos_args = call_args.args
    kwargs = call_args.kwargs

    called_exec_id = (
        kwargs["execution_id"] if "execution_id" in kwargs else (pos_args[0] if len(pos_args) > 0 else None)
    )
    called_lang = (
        kwargs["accept_language"] if "accept_language" in kwargs else (pos_args[1] if len(pos_args) > 1 else None)
    )
    called_profile_id = kwargs["profile_id"] if "profile_id" in kwargs else (pos_args[2] if len(pos_args) > 2 else None)

    assert called_exec_id == report.execution_id
    assert called_lang == report.locale, (
        f"Domain contract violation: accept_language received '{called_lang}' instead of locale '{report.locale}'."
    )
    assert called_profile_id == report.profile_id, (
        f"Domain contract violation: profile_id received '{called_profile_id}' instead of profile '{report.profile_id}'."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_lang", [None, "", "   "])
async def test_synthesis_task_rejects_empty_language(invalid_lang: str | None) -> None:
    """Verify synthesis worker rejects empty or whitespace-only accept_language."""
    with pytest.raises(AppException) as exc_info:
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_1234567890abcdef",
            accept_language=invalid_lang,
            profile_id="prf_01b1d71000000002",
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Strict Fail-Fast Enforced: 'accept_language' is mandatory and cannot be empty." in exc_info.value.message


@pytest.mark.asyncio
async def test_synthesis_task_rejects_locale_as_profile_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify synthesis worker validates real output_profile entity relation and raises ResourceNotFoundError."""
    repo = InMemoryUnifiedWorkflowRepository()
    record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_1234567890abcdef",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        steps=[],
        step_states={},
        profile_syntheses={},
        target_locale="fi",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
    )
    await repo.save_execution(record)
    monkeypatch.setattr("backend_v2.workers.synthesis_worker.get_driver", AsyncMock())
    monkeypatch.setattr("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", lambda driver: repo)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_1234567890abcdef",
            accept_language="fi",
            profile_id="fi",
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert "output_profile with ID 'fi' not found" in exc_info.value.message
