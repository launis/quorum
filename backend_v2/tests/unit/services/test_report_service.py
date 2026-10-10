"""Unit test suite for ReportService verifying full report artifact lifecycle.

Enforces Tripartite Phase Isolation, Four-Tier Pydantic V2 Invariants, and failure containment.
"""

import logging
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.export import ExportPayloadDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.report_artifact import (
    ReportArtifactCreateDTO,
    ReportMetadataDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType, ReportStatus, VisualIntent
from backend_v2.services.report_service import ReportService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_dummy_execution(
    execution_id: str = "exe_1234567890abcdef",
    status: ExecutionStatus = ExecutionStatus.PASSED,
) -> ExecutionRecord:
    reasoning = ReasoningStepDTO(
        step_1_identify_premise="Extract claim.",
        step_2_scan_source="Source text physically contains evidence.",
        step_3_evaluate_anti_patterns="No anti-patterns violated.",
        step_4_final_conclusion="Logic evaluated successfully.",
    )
    atom = ScorecardAtomDTO(
        atom_id="atm_0123456789abcdef",
        level=3,
        level_name="Operational",
        claim_label="Strategic Claim",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=reasoning,
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Sound reasoning.",
        contextual_override=False,
        chart_display_label="Strategic Claim",
        visual_intent=VisualIntent.NEUTRAL,
    )
    step = ExecutionStep(
        id="stp_1",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={"atm_0123456789abcdef": atom},
    )
    return ExecutionRecord(
        id=execution_id,
        workflow_id="wor_0123456789abcdef",
        target_locale="fi",
        status=status,
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        step_states={"stp_1": step},
        profile_syntheses={"prf_1234567890abcdef": RenderedSynthesisCache()},
    )


def _create_dummy_profile(profile_id: str = "prf_1234567890abcdef") -> OutputProfile:
    return OutputProfile(
        id=profile_id,
        slug="executive_report",
        workflow_id="wor_0123456789abcdef",
        name=I18nText(translations={"fi": "Johdon raportti", "en": "Executive Report"}),
        target_block_order=[],
    )


def _create_dummy_report(
    report_id: str = "rep_1234567890abcdef",
    status: ReportStatus = ReportStatus.PENDING,
) -> ReportArtifact:
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
    )


def _create_dummy_report_data_dto() -> ReportDataDTO:
    atom_result = AtomResultDTO(
        tda_id="tda_0123456789abcdef",
        matrix_id="blk_0123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quote="Forensic quote",
        evaluation_reasoning="Sound reasoning.",
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
        results=[atom_result],
        hydrated_references={"tda_0123456789abcdef": hydrated_ref},
    )


@pytest.mark.asyncio
async def test_create_report_artifact_entry_success() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    await repo.save_output_profile(_create_dummy_profile())

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    payload = ReportArtifactCreateDTO(
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
        locale="fi",
    )

    result = await service.create_report_artifact(payload)
    assert result.id.startswith("rep_")
    assert result.execution_id == "exe_1234567890abcdef"
    assert result.status == ReportStatus.PENDING
    assert result.title == "Johdon raportti"

    persisted = await repo.get_report_artifact(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_create_report_artifact_entry_execution_not_found() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_missing", profile_id="prf_1")
    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(payload)


@pytest.mark.asyncio
async def test_create_report_artifact_entry_execution_not_passed() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution(status=ExecutionStatus.RUNNING))
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_1234567890abcdef", profile_id="prf_1")
    with pytest.raises(AppException) as exc_info:
        await service.create_report_artifact(payload)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_create_report_artifact_entry_profile_not_found() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_1234567890abcdef", profile_id="prf_missing")
    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(payload)


@pytest.mark.asyncio
async def test_compile_and_persist_artifact() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq_pool = AsyncMock()

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    await service.compile_and_persist_artifact(report.id, arq_pool)

    job_key = f"compile_report_{report.id}"
    arq_pool.delete.assert_awaited_once_with(f"arq:result:{job_key}")
    updated_rep = await repo.get_report_artifact(report.id)
    assert updated_rep is not None
    assert updated_rep.status == ReportStatus.GENERATING
    arq_pool.enqueue_job.assert_called_once_with(
        "generate_report_artifact_job", report_id=report.id, force_resynthesis=False, _job_id=job_key
    )


@pytest.mark.asyncio
async def test_compile_and_persist_artifact_deduplicated_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Verify that when Arq deduplicates an in-flight job, a structured warning is logged."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq_pool = AsyncMock()
    arq_pool.enqueue_job.return_value = None

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    with caplog.at_level(logging.WARNING):
        await service.compile_and_persist_artifact(report.id, arq_pool)

    job_key = f"compile_report_{report.id}"
    arq_pool.delete.assert_awaited_once_with(f"arq:result:{job_key}")
    assert f"Compilation job '{job_key}' deduplicated by Arq" in caplog.text


@pytest.mark.asyncio
async def test_process_artifact_compilation_success(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution())

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

    # Mock BlueprintTransformer.build_report_dto
    dummy_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
    )
    from backend_v2.services import blueprint

    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    service = ReportService(repo=repo, storage_driver=storage, export_service=export_service, pdf_service=pdf_service)
    await service.process_artifact_compilation(report.id)

    assert storage.save.call_count == 4
    updated_rep = await repo.get_report_artifact(report.id)
    assert updated_rep is not None
    assert updated_rep.status == ReportStatus.READY


@pytest.mark.asyncio
async def test_process_artifact_compilation_failure_isolation() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    # Execution is missing from repo, triggering failure isolation

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    await service.process_artifact_compilation(report.id)

    # Invariant: Failure must set ReportArtifact to FAILED without crashing or mutating ExecutionRecord
    updated_rep = await repo.get_report_artifact(report.id)
    assert updated_rep is not None
    assert updated_rep.status == ReportStatus.FAILED
    assert updated_rep.error_message is not None


@pytest.mark.asyncio
async def test_get_report_sdui_and_streams() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    storage = AsyncMock()
    dummy_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
    )
    storage.read.side_effect = [
        dummy_dto.model_dump_json().encode("utf-8"),
        b"pdf_bytes",
        b"excel_bytes",
        b"csv_bytes",
    ]

    service = ReportService(repo=repo, storage_driver=storage)

    sdui = await service.get_report_sdui(report.id)
    assert isinstance(sdui, ReportDataDTO)

    pdf, fname_pdf = await service.get_report_pdf_bytes(report.id)
    assert pdf == b"pdf_bytes"
    assert fname_pdf.endswith(".pdf")

    excel, fname_excel = await service.get_report_excel_bytes(report.id)
    assert excel == b"excel_bytes"
    assert fname_excel.endswith(".xlsx")

    csv, fname_csv = await service.get_report_csv_bytes(report.id)
    assert csv == b"csv_bytes"
    assert fname_csv.endswith(".csv")


@pytest.mark.asyncio
async def test_get_report_rows() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution())
    storage = AsyncMock()
    storage.read.return_value = _create_dummy_report_data_dto().model_dump_json().encode("utf-8")

    service = ReportService(repo=repo, storage_driver=storage)
    rows = await service.get_report_rows(report.id)
    assert len(rows) == 1
    assert rows[0].metric_key == "blk_0123456789abcdef"
    assert rows[0].metric_label == "Strategic Claim"
    assert rows[0].score == 1.0


@pytest.mark.asyncio
async def test_delete_report_artifact() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    storage = AsyncMock()

    service = ReportService(repo=repo, storage_driver=storage)
    await service.delete_report_artifact(report.id)

    assert storage.delete.call_count == 4
    deleted_rep = await repo.get_report_artifact(report.id)
    assert deleted_rep is None


@pytest.mark.asyncio
async def test_list_and_public_reports() -> None:
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution())
    storage = AsyncMock()
    storage.read.return_value = _create_dummy_report_data_dto().model_dump_json().encode("utf-8")

    service = ReportService(repo=repo, storage_driver=storage)
    summaries = await service.list_reports_for_execution("exe_1234567890abcdef")
    assert len(summaries) == 1
    assert summaries[0].id == report.id

    public = await service.get_public_report(report.id)
    assert public.report_id == report.id
    assert "pdf" in public.downloads
    assert "Strategic Claim" in public.metrics


@pytest.mark.asyncio
async def test_delete_report_artifact_oserror_raises() -> None:
    """Verify delete_report_artifact raises AppException on storage failure."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    storage = AsyncMock()
    storage.delete.side_effect = OSError("Disk write protected")

    service = ReportService(repo=repo, storage_driver=storage)
    with pytest.raises(AppException) as exc_info:
        await service.delete_report_artifact(report.id)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_regenerate_report_artifact() -> None:
    """Verify regenerate_report_artifact enqueues compilation job."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq = AsyncMock()

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    await service.regenerate_report_artifact(report.id, arq)
    arq.enqueue_job.assert_awaited_once()


@pytest.mark.asyncio
async def test_regenerate_report_artifact_clears_stale_arq_result() -> None:
    """Regression test reproducing Arq deduplication deadlock on report regeneration.

    When a report artifact was previously compiled, Arq stores the result under
    'arq:result:compile_report_{report_id}'. When regenerate_report_artifact is called,
    compile_and_persist_artifact enqueues with _job_id=compile_report_{report_id}.
    Arq's enqueue_job checks if arq:result:compile_report_{id} exists and silently returns None.
    Without deleting this stale result key, the compilation job is never enqueued,
    leaving the report permanently trapped in GENERATING status.
    """
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq = AsyncMock()

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    await service.regenerate_report_artifact(report.id, arq)

    job_key = f"compile_report_{report.id}"
    arq.delete.assert_awaited_once_with(f"arq:result:{job_key}")
    arq.enqueue_job.assert_awaited_once_with(
        "generate_report_artifact_job", report_id=report.id, force_resynthesis=True, _job_id=job_key
    )


@pytest.mark.asyncio
async def test_create_report_artifact_workflow_id_mismatch() -> None:
    """Verify create_report_artifact fails fast when profile does not belong to execution workflow."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    mismatched_profile = _create_dummy_profile().model_copy(update={"workflow_id": "wor_other_workflow_123"})
    await repo.save_output_profile(mismatched_profile)

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    payload = ReportArtifactCreateDTO(
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
        locale="fi",
    )

    with pytest.raises(AppException) as exc_info:
        await service.create_report_artifact(payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_returns_existing() -> None:
    """Verify get_or_create_default_artifact returns existing report artifact if already present."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution = _create_dummy_execution()
    await repo.save_execution(execution)
    existing_report = _create_dummy_report()
    await repo.create_report_artifact(existing_report)

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_or_create_default_artifact(
        execution_id=execution.id,
        profile_id="prf_1234567890abcdef",
        locale="fi",
    )

    assert result.id == existing_report.id


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_creates_when_none() -> None:
    """Verify get_or_create_default_artifact creates a new report artifact using execution default profile."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution = _create_dummy_execution().model_copy(update={"output_profile_id": "prf_1234567890abcdef"})
    await repo.save_execution(execution)
    await repo.save_output_profile(_create_dummy_profile())

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_or_create_default_artifact(
        execution_id=execution.id,
    )

    assert result.execution_id == execution.id
    assert result.profile_id == "prf_1234567890abcdef"
    assert result.locale == "fi"
    persisted = await repo.get_report_artifact(result.id)
    assert persisted is not None


@pytest.mark.asyncio
async def test_process_artifact_compilation_syncs_execution_record(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify compilation updates ExecutionRecord.pdf_report_path and sys_render step state."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    execution = _create_dummy_execution()
    await repo.save_execution(execution)

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
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
    )
    from backend_v2.services import blueprint

    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    service = ReportService(repo=repo, storage_driver=storage, export_service=export_service, pdf_service=pdf_service)
    await service.process_artifact_compilation(report.id)

    updated_exec = await repo.get_execution(execution.id)
    assert updated_exec is not None
    assert updated_exec.pdf_report_path == f"artifacts/reports/{report.id}/report.pdf"
    assert updated_exec.step_states is not None
    assert f"sys_render_{report.profile_id}" in updated_exec.step_states
    assert updated_exec.step_states[f"sys_render_{report.profile_id}"].status == ExecutionStatus.PASSED
    assert updated_exec.step_states[f"sys_render_{report.profile_id}"].progress == 100


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_execution_not_found() -> None:
    """Verify get_or_create_default_artifact raises ResourceNotFoundError if execution does not exist."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.get_or_create_default_artifact("exe_nonexistent")


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_workflow_default_and_fallback() -> None:
    """Verify get_or_create_default_artifact resolves workflow default_profile_id and fallback profiles."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution = _create_dummy_execution()
    await repo.save_execution(execution)

    # Case 1: Workflow has default_profile_id
    workflow = Workflow(
        id=execution.workflow_id,
        slug="standard_flow",
        name="Standard Workflow",
        description="Desc",
        status="active",
        version=1,
        default_profile_id="prf_0000000000000001",
        model_registry_id="cfg_model_registry_01",
        historical_context_mode="DISABLED",
    )
    await repo.save_workflow(workflow)
    default_profile = _create_dummy_profile(profile_id="prf_0000000000000001")
    await repo.save_output_profile(default_profile)

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    res1 = await service.get_or_create_default_artifact(execution.id)
    assert res1.profile_id == "prf_0000000000000001"

    # Case 2: Workflow default_profile_id is None, falls back to first matching profile
    repo2 = InMemoryUnifiedWorkflowRepository()
    await repo2.save_execution(execution)
    workflow_no_default = workflow.model_copy(update={"default_profile_id": None})
    await repo2.save_workflow(workflow_no_default)
    fallback_profile = _create_dummy_profile(profile_id="prf_0000000000000002")
    await repo2.save_output_profile(fallback_profile)

    service2 = ReportService(repo=repo2, storage_driver=AsyncMock())
    res2 = await service2.get_or_create_default_artifact(execution.id)
    assert res2.profile_id == "prf_0000000000000002"

    # Case 3: No matching profiles raises ResourceNotFoundError
    repo3 = InMemoryUnifiedWorkflowRepository()
    await repo3.save_execution(execution)
    await repo3.save_workflow(workflow_no_default)

    service3 = ReportService(repo=repo3, storage_driver=AsyncMock())
    with pytest.raises(ResourceNotFoundError):
        await service3.get_or_create_default_artifact(execution.id)


@pytest.mark.asyncio
async def test_process_artifact_compilation_missing_report_raises() -> None:
    """Verify process_artifact_compilation raises ResourceNotFoundError if report does not exist."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.process_artifact_compilation("rep_missing")


@pytest.mark.asyncio
async def test_read_artifact_failures() -> None:
    """Verify _read_artifact raises AppException when not ready or storage read fails."""
    repo = InMemoryUnifiedWorkflowRepository()
    pending_report = _create_dummy_report(status=ReportStatus.PENDING)
    ready_report = _create_dummy_report(status=ReportStatus.READY)

    storage = AsyncMock()
    storage.read.side_effect = OSError("Read failed")

    service = ReportService(repo=repo, storage_driver=storage)

    with pytest.raises(AppException) as exc_info1:
        await service._read_artifact(pending_report, "artifacts/reports/rep_1/report.pdf", "PDF")
    assert exc_info1.value.status_code == 409

    with pytest.raises(AppException) as exc_info2:
        await service._read_artifact(ready_report, "artifacts/reports/rep_1/report.pdf", "PDF")
    assert exc_info2.value.status_code == 500


@pytest.mark.asyncio
async def test_get_public_report_execution_missing_raises() -> None:
    """Verify get_public_report raises ResourceNotFoundError if underlying execution is missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    with pytest.raises(ResourceNotFoundError):
        await service.get_public_report(report.id)


@pytest.mark.asyncio
async def test_process_artifact_compilation_idempotent_when_ready() -> None:
    """Verify process_artifact_compilation short-circuits when status is READY and PDF exists."""
    repo = InMemoryUnifiedWorkflowRepository()
    storage = AsyncMock()
    storage.exists.return_value = True

    paths = ReportStoragePathsDTO(pdf_path="artifacts/reports/rep_123/report.pdf")
    report = _create_dummy_report(status=ReportStatus.READY)
    report = report.model_copy(update={"storage_paths": paths})
    await repo.create_report_artifact(report)

    service = ReportService(repo=repo, storage_driver=storage)
    await service.process_artifact_compilation(report.id)

    persisted = await repo.get_report_artifact(report.id)
    assert persisted is not None
    assert persisted.status == ReportStatus.READY
    storage.exists.assert_awaited_once_with("artifacts/reports/rep_123/report.pdf")


@pytest.mark.asyncio
async def test_process_artifact_compilation_force_resynthesis_false_retains_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify force_resynthesis=False retains cached profile synthesis without calling runner."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution())

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
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
    )
    from backend_v2.services import blueprint

    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))
    synthesis_runner = AsyncMock()

    service = ReportService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
        synthesis_runner=synthesis_runner,
    )
    await service.process_artifact_compilation(report.id, force_resynthesis=False)

    synthesis_runner.assert_not_called()
    execution = await repo.get_execution(report.execution_id)
    assert execution is not None
    assert report.profile_id in execution.profile_syntheses


@pytest.mark.asyncio
async def test_process_artifact_compilation_force_resynthesis_true_invalidates_cache_and_invokes_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify force_resynthesis=True prunes cache and triggers synthesis_runner."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution())

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
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
    )
    from backend_v2.services import blueprint

    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    async def mock_runner(execution_id: str, accept_language: str, profile_id: str) -> None:
        exec_record = await repo.get_execution(execution_id)
        if exec_record:
            from backend_v2.models.domain.synthesis import RenderedSynthesisCache
            from backend_v2.models.dtos.trace import ExecutionUpdateDTO

            new_syntheses = {
                **exec_record.profile_syntheses,
                profile_id: RenderedSynthesisCache(variance_explanation="Fresh re-synthesized text"),
            }
            await repo.update_execution(execution_id, ExecutionUpdateDTO(profile_syntheses=new_syntheses))

    synthesis_runner = AsyncMock(side_effect=mock_runner)

    service = ReportService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
        synthesis_runner=synthesis_runner,
    )
    await service.process_artifact_compilation(report.id, force_resynthesis=True)

    synthesis_runner.assert_awaited_once_with(
        execution_id=report.execution_id,
        accept_language=report.locale,
        profile_id=report.profile_id,
    )
    execution = await repo.get_execution(report.execution_id)
    assert execution is not None
    assert report.profile_id in execution.profile_syntheses
    assert execution.profile_syntheses[report.profile_id].variance_explanation == "Fresh re-synthesized text"


@pytest.mark.asyncio
async def test_process_artifact_compilation_force_resynthesis_bypasses_ready_idempotency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify force_resynthesis=True does not early-return on READY status with existing files."""
    repo = InMemoryUnifiedWorkflowRepository()
    storage = AsyncMock()
    storage.exists.return_value = True
    storage.save.side_effect = lambda path, data: path

    paths = ReportStoragePathsDTO(pdf_path="artifacts/reports/rep_123/report.pdf")
    report = _create_dummy_report(status=ReportStatus.READY)
    report = report.model_copy(update={"storage_paths": paths})
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution())

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
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
    )
    from backend_v2.services import blueprint

    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    async def mock_runner(execution_id: str, accept_language: str, profile_id: str) -> None:
        exec_record = await repo.get_execution(execution_id)
        if exec_record:
            from backend_v2.models.domain.synthesis import RenderedSynthesisCache
            from backend_v2.models.dtos.trace import ExecutionUpdateDTO

            new_syntheses = {
                **exec_record.profile_syntheses,
                profile_id: RenderedSynthesisCache(variance_explanation="Regenerated text"),
            }
            await repo.update_execution(execution_id, ExecutionUpdateDTO(profile_syntheses=new_syntheses))

    synthesis_runner = AsyncMock(side_effect=mock_runner)

    service = ReportService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
        synthesis_runner=synthesis_runner,
    )
    await service.process_artifact_compilation(report.id, force_resynthesis=True)

    assert storage.save.call_count == 4
