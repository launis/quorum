"""Unit test suite for ReportLifecycleService verifying CRUD, default resolution, regeneration, and public summaries."""

import logging
from datetime import UTC, datetime
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
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.report_artifact import (
    ReportArtifactCreateDTO,
    ReportMetadataDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    HistoricalContextMode,
    LaxSDUIComponentType,
    ReportStatus,
    VisualIntent,
)
from backend_v2.services.report.lifecycle_service import ReportLifecycleService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_dummy_execution(
    execution_id: str = "exe_0195f3a0000070018234567890abcdef",
    status: ExecutionStatus = ExecutionStatus.PASSED,
) -> ExecutionRecord:
    reasoning = ReasoningStepDTO(
        step_1_identify_premise="Extract claim.",
        step_2_scan_source="Source text physically contains evidence.",
        step_3_evaluate_anti_patterns="No anti-patterns violated.",
        step_4_final_conclusion="Logic evaluated successfully.",
    )
    atom = ScorecardAtomDTO(
        atom_id="atm_0195f3a0000070008123456789abcdef",
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
        scorecard_atoms={"atm_0195f3a0000070008123456789abcdef": atom},
    )
    return ExecutionRecord(
        id=execution_id,
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        target_locale="fi",
        status=status,
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        step_states={"stp_1": step},
        profile_syntheses={
            "prf_0195f3a0000070018234567890abcdef": RenderedSynthesisCache(variance_explanation="Executive summary")
        },
    )


def _create_dummy_profile(profile_id: str = "prf_0195f3a0000070018234567890abcdef") -> OutputProfile:
    return OutputProfile(
        id=profile_id,
        slug="executive_report",
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        name=I18nText(translations={"fi": "Johdon raportti", "en": "Executive Report"}),
        target_block_order=[],
    )


def _create_dummy_report(
    report_id: str = "rep_0195f3a0000070018234567890abcdef",
    status: ReportStatus = ReportStatus.PENDING,
) -> ReportArtifact:
    now = datetime.now(UTC)
    return ReportArtifact(
        id=report_id,
        execution_id="exe_0195f3a0000070018234567890abcdef",
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        profile_id="prf_0195f3a0000070018234567890abcdef",
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
    atom_result = AtomResultDTO(
        tda_id="tda_0195f3a0000070008123456789abcdef",
        matrix_id="blk_0195f3a0000070008123456789abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes=("Forensic quote",),
        evaluation_reasoning="Sound reasoning.",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Strategic Claim",
    )
    return ReportDataDTO(
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        execution_id="exe_0195f3a0000070018234567890abcdef",
        profile_id="prf_0195f3a0000070018234567890abcdef",
        global_score=4.0,
        has_warning=False,
        inner_sdui_blocks=[],
        results=[atom_result],
        hydrated_references={"tda_0195f3a0000070008123456789abcdef": hydrated_ref},
    )


@pytest.mark.asyncio
async def test_get_report_success() -> None:
    """Verify get_report returns existing ReportArtifact matching repository state."""
    repo = InMemoryUnifiedWorkflowRepository()
    expected_report = _create_dummy_report(report_id="rep_0195f3a0000070018234567890abcdef")
    await repo.create_report_artifact(expected_report)

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_report("rep_0195f3a0000070018234567890abcdef")

    assert result.id == "rep_0195f3a0000070018234567890abcdef"
    assert result.execution_id == expected_report.execution_id
    assert result.profile_id == expected_report.profile_id


@pytest.mark.asyncio
async def test_get_report_not_found() -> None:
    """Verify get_report raises ResourceNotFoundError with ErrorCodes.RESOURCE_NOT_FOUND when missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await service.get_report("rep_0195f3a0000070008000000000000000")

    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_create_report_artifact_persists_model() -> None:
    """Verify create_report_artifact creates, persists, and returns ReportArtifact with Opaque Stripe ID."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    await repo.save_output_profile(_create_dummy_profile())

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    payload = ReportArtifactCreateDTO(
        execution_id="exe_0195f3a0000070018234567890abcdef",
        profile_id="prf_0195f3a0000070018234567890abcdef",
        locale="fi",
    )

    result = await service.create_report_artifact(payload)
    assert result.id.startswith("rep_")
    assert result.execution_id == "exe_0195f3a0000070018234567890abcdef"
    assert result.status == ReportStatus.PENDING
    assert result.title == "Johdon raportti"

    persisted = await repo.get_report_artifact(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_create_report_artifact_entry_success() -> None:
    """Verify create_report_artifact succeeds for valid passed execution and profile."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    await repo.save_output_profile(_create_dummy_profile())

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    payload = ReportArtifactCreateDTO(
        execution_id="exe_0195f3a0000070018234567890abcdef",
        profile_id="prf_0195f3a0000070018234567890abcdef",
        locale="fi",
    )

    result = await service.create_report_artifact(payload)
    assert result.id.startswith("rep_")
    assert result.execution_id == "exe_0195f3a0000070018234567890abcdef"
    assert result.status == ReportStatus.PENDING
    assert result.title == "Johdon raportti"

    persisted = await repo.get_report_artifact(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_create_report_artifact_entry_execution_not_found() -> None:
    """Verify create_report_artifact raises ResourceNotFoundError when execution is missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_missing", profile_id="prf_1")
    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(payload)


@pytest.mark.asyncio
async def test_create_report_artifact_entry_execution_not_passed() -> None:
    """Verify create_report_artifact raises 409 AppException when execution is not PASSED."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution(status=ExecutionStatus.RUNNING))
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_0195f3a0000070018234567890abcdef", profile_id="prf_1")
    with pytest.raises(AppException) as exc_info:
        await service.create_report_artifact(payload)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_create_report_artifact_entry_profile_not_found() -> None:
    """Verify create_report_artifact raises ResourceNotFoundError when output profile is missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_0195f3a0000070018234567890abcdef", profile_id="prf_missing")
    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(payload)


@pytest.mark.asyncio
async def test_create_report_artifact_workflow_id_mismatch() -> None:
    """Verify create_report_artifact fails fast when profile does not belong to execution workflow."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    mismatched_profile = _create_dummy_profile().model_copy(update={"workflow_id": "wor_other_workflow_123"})
    await repo.save_output_profile(mismatched_profile)

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    payload = ReportArtifactCreateDTO(
        execution_id="exe_0195f3a0000070018234567890abcdef",
        profile_id="prf_0195f3a0000070018234567890abcdef",
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

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_or_create_default_artifact(
        execution_id=execution.id,
        profile_id="prf_0195f3a0000070018234567890abcdef",
        locale="fi",
    )

    assert result.id == existing_report.id


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_creates_when_none() -> None:
    """Verify get_or_create_default_artifact creates a new report artifact using execution default profile."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution = _create_dummy_execution().model_copy(
        update={"output_profile_id": "prf_0195f3a0000070018234567890abcdef"}
    )
    await repo.save_execution(execution)
    await repo.save_output_profile(_create_dummy_profile())

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_or_create_default_artifact(
        execution_id=execution.id,
    )

    assert result.execution_id == execution.id
    assert result.profile_id == "prf_0195f3a0000070018234567890abcdef"
    assert result.locale == "fi"
    persisted = await repo.get_report_artifact(result.id)
    assert persisted is not None


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_execution_not_found() -> None:
    """Verify get_or_create_default_artifact raises ResourceNotFoundError if execution does not exist."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.get_or_create_default_artifact("exe_nonexistent")


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_workflow_default_and_fallback() -> None:
    """Verify get_or_create_default_artifact resolves workflow default_profile_id and fallback profiles."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution = _create_dummy_execution()
    await repo.save_execution(execution)

    # Active profile ID resolution
    exec_active = execution.model_copy(update={"active_profile_id": "prf_0195f3a0000070018234567890abcdef"})
    await repo.save_execution(exec_active)
    await repo.save_output_profile(_create_dummy_profile())
    service_active = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    created_active = await service_active.get_or_create_default_artifact(exec_active.id)
    assert created_active.profile_id == "prf_0195f3a0000070018234567890abcdef"

    # Case 1: Workflow has default_profile_id
    repo1 = InMemoryUnifiedWorkflowRepository()
    await repo1.save_execution(execution)
    workflow = Workflow(
        id=execution.workflow_id,
        slug="standard_flow",
        name="Standard Workflow",
        description="Desc",
        status="active",
        version=1,
        default_profile_id="prf_0195f3a0000070008000000000000001",
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
    )
    await repo1.save_workflow(workflow)
    default_profile = _create_dummy_profile(profile_id="prf_0195f3a0000070008000000000000001")
    await repo1.save_output_profile(default_profile)

    service1 = ReportLifecycleService(repo=repo1, storage_driver=AsyncMock())
    res1 = await service1.get_or_create_default_artifact(execution.id)
    assert res1.profile_id == "prf_0195f3a0000070008000000000000001"

    # Case 2: Workflow default_profile_id is None, falls back to first matching profile
    repo2 = InMemoryUnifiedWorkflowRepository()
    await repo2.save_execution(execution)
    workflow_no_default = workflow.model_copy(update={"default_profile_id": None})
    await repo2.save_workflow(workflow_no_default)
    fallback_profile = _create_dummy_profile(profile_id="prf_0195f3a0000070008000000000000002")
    await repo2.save_output_profile(fallback_profile)

    service2 = ReportLifecycleService(repo=repo2, storage_driver=AsyncMock())
    res2 = await service2.get_or_create_default_artifact(execution.id)
    assert res2.profile_id == "prf_0195f3a0000070008000000000000002"

    # Case 3: No matching profiles or missing workflow raises ResourceNotFoundError
    repo3 = InMemoryUnifiedWorkflowRepository()
    await repo3.save_execution(execution)
    service3 = ReportLifecycleService(repo=repo3, storage_driver=AsyncMock())
    with pytest.raises(ResourceNotFoundError):
        await service3.get_or_create_default_artifact(execution.id)

    await repo3.save_workflow(workflow_no_default)
    with pytest.raises(ResourceNotFoundError):
        await service3.get_or_create_default_artifact(execution.id)


@pytest.mark.asyncio
async def test_delete_report_artifact() -> None:
    """Verify delete_report_artifact removes storage files and repository record."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    storage = AsyncMock()
    storage.delete.side_effect = [FileNotFoundError(), None, None, None]

    service = ReportLifecycleService(repo=repo, storage_driver=storage)
    await service.delete_report_artifact(report.id)

    assert storage.delete.call_count == 4
    deleted_rep = await repo.get_report_artifact(report.id)
    assert deleted_rep is None


@pytest.mark.asyncio
async def test_delete_report_artifact_oserror_raises() -> None:
    """Verify delete_report_artifact raises AppException on storage failure."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    storage = AsyncMock()
    storage.delete.side_effect = OSError("Disk write protected")

    service = ReportLifecycleService(repo=repo, storage_driver=storage)
    with pytest.raises(AppException) as exc_info:
        await service.delete_report_artifact(report.id)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_regenerate_report_artifact(caplog: pytest.LogCaptureFixture) -> None:
    """Verify regenerate_report_artifact enqueues compilation job and logs deduplication warning."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq = AsyncMock()
    arq.enqueue_job.return_value = None

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    with caplog.at_level(logging.WARNING):
        await service.regenerate_report_artifact(report.id, arq)
    arq.enqueue_job.assert_awaited_once()
    assert f"compile_report_{report.id}" in caplog.text


@pytest.mark.asyncio
async def test_regenerate_report_artifact_clears_stale_arq_result() -> None:
    """Regression test reproducing Arq deduplication deadlock on report regeneration."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)
    arq = AsyncMock()

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    await service.regenerate_report_artifact(report.id, arq)

    job_key = f"compile_report_{report.id}"
    arq.delete.assert_awaited_once_with(f"arq:result:{job_key}")
    arq.enqueue_job.assert_awaited_once_with(
        "generate_report_artifact_job", report_id=report.id, force_resynthesis=True, _job_id=job_key
    )


@pytest.mark.asyncio
async def test_list_and_public_reports() -> None:
    """Verify list_reports_for_execution and get_public_report success and error branches."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)
    await repo.save_execution(_create_dummy_execution())
    storage = AsyncMock()
    storage.read.return_value = _create_dummy_report_data_dto().model_dump_json().encode("utf-8")

    service = ReportLifecycleService(repo=repo, storage_driver=storage)
    summaries = await service.list_reports_for_execution("exe_0195f3a0000070018234567890abcdef")
    assert len(summaries) == 1
    assert summaries[0].id == report.id

    public = await service.get_public_report(report.id)
    assert public.report_id == report.id
    assert "pdf" in public.downloads
    assert "Strategic Claim" in public.metrics
    assert public.executive_summary_markdown == "Executive summary"

    # Storage OSError raises AppException 500
    storage.read.side_effect = OSError("Storage failure")
    with pytest.raises(AppException) as exc_500:
        await service.get_public_report(report.id)
    assert exc_500.value.status_code == 500

    # Pending report raises AppException 409
    pending = _create_dummy_report(report_id="rep_0195f3a0000070008000000000000009", status=ReportStatus.PENDING)
    await repo.create_report_artifact(pending)
    with pytest.raises(AppException) as exc_409:
        await service.get_public_report(pending.id)
    assert exc_409.value.status_code == 409


@pytest.mark.asyncio
async def test_get_public_report_execution_missing_raises() -> None:
    """Verify get_public_report raises ResourceNotFoundError if underlying execution is missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    with pytest.raises(ResourceNotFoundError):
        await service.get_public_report(report.id)
