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
async def test_compile_and_persist_artifact_not_found_and_deduplicated(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify compile_and_persist_artifact raises ResourceNotFoundError and logs warning on deduplication."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportCompilationService(repo=repo, storage_driver=AsyncMock())
    arq_pool = AsyncMock()

    with pytest.raises(ResourceNotFoundError):
        await service.compile_and_persist_artifact("rep_0000000000000000", arq_pool)

    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq_pool.enqueue_job.return_value = None

    with caplog.at_level(logging.WARNING):
        await service.compile_and_persist_artifact(report.id, arq_pool)
    assert f"compile_report_{report.id}" in caplog.text


@pytest.mark.asyncio
async def test_process_artifact_compilation_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify idempotency, force_resynthesis runner invocation, missing synthesis runner failure, and missing report."""
    repo = InMemoryUnifiedWorkflowRepository()
    storage = AsyncMock()
    service = ReportCompilationService(repo=repo, storage_driver=storage)

    # 1. Missing report raises ResourceNotFoundError
    with pytest.raises(ResourceNotFoundError):
        await service.process_artifact_compilation("rep_0000000000000000")

    # 2. Idempotent skip when READY and PDF exists
    ready_report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(ready_report)
    storage.exists.return_value = True
    await service.process_artifact_compilation(ready_report.id)
    storage.exists.assert_awaited_once()

    # 3. Missing execution dispatches to DLQ (FAILED status)
    pending_report = _create_dummy_report(report_id="rep_0000000000000002", status=ReportStatus.PENDING)
    await repo.create_report_artifact(pending_report)
    await service.process_artifact_compilation(pending_report.id)
    failed_rep = await repo.get_report_artifact(pending_report.id)
    assert failed_rep is not None
    assert failed_rep.status == ReportStatus.FAILED

    # 4. Missing profile synthesis without synthesis_runner dispatches to DLQ
    exec_no_synth = _create_dummy_execution().model_copy(update={"profile_syntheses": {}})
    await repo.save_execution(exec_no_synth)
    report_no_runner = _create_dummy_report(report_id="rep_0000000000000003", status=ReportStatus.PENDING)
    await repo.create_report_artifact(report_no_runner)
    await service.process_artifact_compilation(report_no_runner.id)
    failed_no_runner = await repo.get_report_artifact(report_no_runner.id)
    assert failed_no_runner is not None
    assert failed_no_runner.status == ReportStatus.FAILED

    # 5. force_resynthesis=True invalidates cache and runs synthesis_runner
    await repo.save_execution(_create_dummy_execution())
    report_resynth = _create_dummy_report(report_id="rep_0000000000000004", status=ReportStatus.PENDING)
    await repo.create_report_artifact(report_resynth)

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
        exec_rec = await repo.get_execution(execution_id)
        if exec_rec:
            updated_syntheses = {
                **exec_rec.profile_syntheses,
                profile_id: RenderedSynthesisCache(variance_explanation="Resynthesized"),
            }
            await repo.update_execution(execution_id, ExecutionUpdateDTO(profile_syntheses=updated_syntheses))

    runner = AsyncMock(side_effect=mock_runner)
    service_with_runner = ReportCompilationService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
        synthesis_runner=runner,
    )
    await service_with_runner.process_artifact_compilation(report_resynth.id, force_resynthesis=True)
    runner.assert_awaited_once()
    final_rep = await repo.get_report_artifact(report_resynth.id)
    assert final_rep is not None
    assert final_rep.status == ReportStatus.READY
