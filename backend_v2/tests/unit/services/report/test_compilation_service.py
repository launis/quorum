"""Unit test suite for ReportCompilationService verifying multi-format compilation, synthesis, and DLQ isolation."""

import logging
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import ExecutionNotReadyError, ResourceNotFoundError
from backend_v2.models.domain.execution import ExecutionMetadata, ExecutionRecord, ExecutionStep, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.export import ExportPayloadDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.report_artifact import (
    ReportMetadataDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    LLMProvider,
    ReportStatus,
    VisualIntent,
)
from backend_v2.services import blueprint
from backend_v2.services.report.compilation_service import ReportCompilationService
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
        structural_location="Section 1",
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
        metadata=ExecutionMetadata(
            provider_override=LLMProvider.VERTEX_AI,
            model_registry_id="cfg_model_registry_01",
        ),
    )


def _create_dummy_report(
    report_id: str = "rep_1234567890abcdef",
    status: ReportStatus = ReportStatus.PENDING,
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


@pytest.mark.asyncio
async def test_compile_and_persist_artifact() -> None:
    """Verify compile_and_persist_artifact sets GENERATING status and enqueues Arq job."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq_pool = AsyncMock()

    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())
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

    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())
    with caplog.at_level(logging.WARNING):
        await service.compile_and_persist_artifact(report.id, arq_pool)

    job_key = f"compile_report_{report.id}"
    arq_pool.delete.assert_awaited_once_with(f"arq:result:{job_key}")
    assert f"Compilation job '{job_key}' deduplicated by Arq" in caplog.text


@pytest.mark.asyncio
async def test_compile_and_persist_artifact_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify full compilation pipeline compiles SDUI, PDF, XLSX, and CSV payloads and updates status."""
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
    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    arq_pool = AsyncMock()
    service = ReportCompilationService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
    )

    await service.compile_and_persist_artifact(report.id, arq_pool)
    generating_rep = await repo.get_report_artifact(report.id)
    assert generating_rep is not None
    assert generating_rep.status == ReportStatus.GENERATING

    await service.process_artifact_compilation(report.id)
    assert storage.save.call_count == 4
    completed_rep = await repo.get_report_artifact(report.id)
    assert completed_rep is not None
    assert completed_rep.status == ReportStatus.READY
    assert completed_rep.metadata.provider == LLMProvider.VERTEX_AI.value
    assert completed_rep.metadata.model_registry_id == "cfg_model_registry_01"


@pytest.mark.asyncio
async def test_compile_execution_not_ready() -> None:
    """Verify compile_and_persist_artifact raises ExecutionNotReadyError when ExecutionRecord is in RUNNING status."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution(status=ExecutionStatus.RUNNING))

    arq_pool = AsyncMock()
    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ExecutionNotReadyError):
        await service.compile_and_persist_artifact(report.id, arq_pool)


@pytest.mark.asyncio
async def test_compile_and_persist_artifact_not_found() -> None:
    """Verify compile_and_persist_artifact raises ResourceNotFoundError when report is missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())
    arq_pool = AsyncMock()

    with pytest.raises(ResourceNotFoundError):
        await service.compile_and_persist_artifact("rep_0000000000000000", arq_pool)


@pytest.mark.asyncio
async def test_process_artifact_compilation_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify process_artifact_compilation saves all 4 format files and transitions report to READY."""
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
    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    service = ReportCompilationService(
        repo=repo, storage_driver=storage, export_service=export_service, pdf_service=pdf_service
    )
    await service.process_artifact_compilation(report.id)

    assert storage.save.call_count == 4
    updated_rep = await repo.get_report_artifact(report.id)
    assert updated_rep is not None
    assert updated_rep.status == ReportStatus.READY


@pytest.mark.asyncio
async def test_process_artifact_compilation_failure_isolation() -> None:
    """Verify failure sets ReportArtifact to FAILED without crashing or mutating ExecutionRecord."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)

    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())
    await service.process_artifact_compilation(report.id)

    updated_rep = await repo.get_report_artifact(report.id)
    assert updated_rep is not None
    assert updated_rep.status == ReportStatus.FAILED
    assert updated_rep.error_message is not None


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
    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    service = ReportCompilationService(
        repo=repo, storage_driver=storage, export_service=export_service, pdf_service=pdf_service
    )
    await service.process_artifact_compilation(report.id)

    updated_exec = await repo.get_execution(execution.id)
    assert updated_exec is not None
    assert updated_exec.pdf_report_path == f"artifacts/reports/{report.id}/report.pdf"
    assert updated_exec.step_states is not None
    assert f"sys_render_{report.profile_id}" in updated_exec.step_states
    assert updated_exec.step_states[f"sys_render_{report.profile_id}"].status == ExecutionStatus.PASSED
    assert updated_exec.step_states[f"sys_render_{report.profile_id}"].progress == 100


@pytest.mark.asyncio
async def test_process_artifact_compilation_missing_report_raises() -> None:
    """Verify process_artifact_compilation raises ResourceNotFoundError if report does not exist."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.process_artifact_compilation("rep_missing")


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

    service = ReportCompilationService(repo=repo, storage_driver=storage)
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
    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))
    synthesis_runner = AsyncMock()

    service = ReportCompilationService(
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
    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    async def mock_runner(execution_id: str, accept_language: str, profile_id: str) -> None:
        exec_record = await repo.get_execution(execution_id)
        if exec_record:
            new_syntheses = {
                **exec_record.profile_syntheses,
                profile_id: RenderedSynthesisCache(variance_explanation="Fresh re-synthesized text"),
            }
            await repo.update_execution(execution_id, ExecutionUpdateDTO(profile_syntheses=new_syntheses))

    synthesis_runner = AsyncMock(side_effect=mock_runner)

    service = ReportCompilationService(
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
    monkeypatch.setattr(blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=dummy_dto))

    async def mock_runner(execution_id: str, accept_language: str, profile_id: str) -> None:
        exec_record = await repo.get_execution(execution_id)
        if exec_record:
            new_syntheses = {
                **exec_record.profile_syntheses,
                profile_id: RenderedSynthesisCache(variance_explanation="Regenerated text"),
            }
            await repo.update_execution(execution_id, ExecutionUpdateDTO(profile_syntheses=new_syntheses))

    synthesis_runner = AsyncMock(side_effect=mock_runner)

    service = ReportCompilationService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
        synthesis_runner=synthesis_runner,
    )
    await service.process_artifact_compilation(report.id, force_resynthesis=True)

    assert storage.save.call_count == 4


@pytest.mark.asyncio
async def test_process_artifact_compilation_missing_runner_dispatches_dlq() -> None:
    """Verify missing profile synthesis without synthesis_runner dispatches to DLQ."""
    repo = InMemoryUnifiedWorkflowRepository()
    exec_no_synth = _create_dummy_execution().model_copy(update={"profile_syntheses": {}})
    await repo.save_execution(exec_no_synth)
    report_no_runner = _create_dummy_report(report_id="rep_0000000000000003", status=ReportStatus.PENDING)
    await repo.create_report_artifact(report_no_runner)

    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())
    await service.process_artifact_compilation(report_no_runner.id)
    failed_no_runner = await repo.get_report_artifact(report_no_runner.id)
    assert failed_no_runner is not None
    assert failed_no_runner.status == ReportStatus.FAILED
