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
        profile_syntheses={"prf_1234567890abcdef": RenderedSynthesisCache(variance_explanation="Executive summary")},
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
    atom_result = AtomResultDTO(
        tda_id="tda_0123456789abcdef",
        matrix_id="blk_0123456789abcdef",
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
async def test_get_report_success() -> None:
    """Verify get_report returns existing ReportArtifact matching repository state."""
    repo = InMemoryUnifiedWorkflowRepository()
    expected_report = _create_dummy_report(report_id="rep_1234567890abcdef")
    await repo.create_report_artifact(expected_report)

    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_report("rep_1234567890abcdef")

    assert result.id == "rep_1234567890abcdef"
    assert result.execution_id == expected_report.execution_id
    assert result.profile_id == expected_report.profile_id


@pytest.mark.asyncio
async def test_get_report_not_found() -> None:
    """Verify get_report raises ResourceNotFoundError with ErrorCodes.RESOURCE_NOT_FOUND when missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await service.get_report("rep_0000000000000000")

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
async def test_create_report_artifact_error_branches() -> None:
    """Verify create_report_artifact fails fast on missing execution, non-passed execution, missing/mismatched profile."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(ReportArtifactCreateDTO(execution_id="exe_missing", profile_id="prf_1"))

    await repo.save_execution(_create_dummy_execution(status=ExecutionStatus.RUNNING))
    with pytest.raises(AppException) as exc_not_ready:
        await service.create_report_artifact(
            ReportArtifactCreateDTO(execution_id="exe_1234567890abcdef", profile_id="prf_1")
        )
    assert exc_not_ready.value.status_code == 409

    await repo.save_execution(_create_dummy_execution(status=ExecutionStatus.PASSED))
    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(
            ReportArtifactCreateDTO(execution_id="exe_1234567890abcdef", profile_id="prf_missing")
        )

    mismatched_profile = _create_dummy_profile().model_copy(update={"workflow_id": "wor_other_workflow_123"})
    await repo.save_output_profile(mismatched_profile)
    with pytest.raises(AppException) as exc_mismatch:
        await service.create_report_artifact(
            ReportArtifactCreateDTO(execution_id="exe_1234567890abcdef", profile_id="prf_1234567890abcdef")
        )
    assert exc_mismatch.value.status_code == 400


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_branches() -> None:
    """Verify get_or_create_default_artifact resolves existing, output_profile_id, active_profile_id, and workflow defaults."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportLifecycleService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.get_or_create_default_artifact("exe_nonexistent")

    # Missing workflow raises ResourceNotFoundError
    execution = _create_dummy_execution()
    await repo.save_execution(execution)
    with pytest.raises(ResourceNotFoundError):
        await service.get_or_create_default_artifact(execution.id)

    # Active profile ID resolution
    exec_active = execution.model_copy(update={"active_profile_id": "prf_1234567890abcdef"})
    await repo.save_execution(exec_active)
    await repo.save_output_profile(_create_dummy_profile())
    created = await service.get_or_create_default_artifact(exec_active.id)
    assert created.profile_id == "prf_1234567890abcdef"

    # Existing report returned immediately
    existing = await service.get_or_create_default_artifact(exec_active.id, profile_id="prf_1234567890abcdef")
    assert existing.id == created.id

    # Workflow default_profile_id resolution
    repo2 = InMemoryUnifiedWorkflowRepository()
    await repo2.save_execution(execution)
    workflow = Workflow(
        id=execution.workflow_id,
        slug="standard_flow",
        name="Standard Workflow",
        description="Desc",
        status="active",
        version=1,
        default_profile_id="prf_0000000000000001",
        model_registry_id="cfg_model_registry_01",
        historical_context_mode=HistoricalContextMode.DISABLED,
    )
    await repo2.save_workflow(workflow)
    await repo2.save_output_profile(_create_dummy_profile(profile_id="prf_0000000000000001"))
    service2 = ReportLifecycleService(repo=repo2, storage_driver=AsyncMock())
    res_wf = await service2.get_or_create_default_artifact(execution.id)
    assert res_wf.profile_id == "prf_0000000000000001"

    # Workflow fallback to matching profile and error when none
    repo3 = InMemoryUnifiedWorkflowRepository()
    await repo3.save_execution(execution)
    await repo3.save_workflow(workflow.model_copy(update={"default_profile_id": None}))
    service3 = ReportLifecycleService(repo=repo3, storage_driver=AsyncMock())
    with pytest.raises(ResourceNotFoundError):
        await service3.get_or_create_default_artifact(execution.id)

    await repo3.save_output_profile(_create_dummy_profile(profile_id="prf_0000000000000002"))
    res_fallback = await service3.get_or_create_default_artifact(execution.id)
    assert res_fallback.profile_id == "prf_0000000000000002"


@pytest.mark.asyncio
async def test_delete_and_regenerate_report_artifact(caplog: pytest.LogCaptureFixture) -> None:
    """Verify delete_report_artifact handles FileNotFoundError/OSError and regenerate_report_artifact enqueues job."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report()
    await repo.create_report_artifact(report)

    storage = AsyncMock()
    storage.delete.side_effect = [FileNotFoundError(), None, None, None]
    service = ReportLifecycleService(repo=repo, storage_driver=storage)

    arq = AsyncMock()
    arq.enqueue_job.return_value = None
    with caplog.at_level(logging.WARNING):
        await service.regenerate_report_artifact(report.id, arq)
    assert f"compile_report_{report.id}" in caplog.text

    await service.delete_report_artifact(report.id)
    assert await repo.get_report_artifact(report.id) is None

    # OSError during delete raises AppException
    await repo.create_report_artifact(report)
    storage.delete.side_effect = OSError("Disk error")
    with pytest.raises(AppException) as exc_info:
        await service.delete_report_artifact(report.id)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_list_and_get_public_report() -> None:
    """Verify list_reports_for_execution and get_public_report success and error branches."""
    repo = InMemoryUnifiedWorkflowRepository()
    report = _create_dummy_report(status=ReportStatus.READY)
    await repo.create_report_artifact(report)

    storage = AsyncMock()
    service = ReportLifecycleService(repo=repo, storage_driver=storage)

    # Missing execution raises ResourceNotFoundError
    with pytest.raises(ResourceNotFoundError):
        await service.get_public_report(report.id)

    await repo.save_execution(_create_dummy_execution())

    # Storage OSError raises AppException 500
    storage.read.side_effect = OSError("Storage failure")
    with pytest.raises(AppException) as exc_500:
        await service.get_public_report(report.id)
    assert exc_500.value.status_code == 500

    # Pending report raises AppException 409
    pending = _create_dummy_report(report_id="rep_0000000000000009", status=ReportStatus.PENDING)
    await repo.create_report_artifact(pending)
    with pytest.raises(AppException) as exc_409:
        await service.get_public_report(pending.id)
    assert exc_409.value.status_code == 409

    # Valid READY report returns PublicReportDTO
    storage.read.side_effect = None
    storage.read.return_value = _create_dummy_report_data_dto().model_dump_json().encode("utf-8")
    summaries = await service.list_reports_for_execution("exe_1234567890abcdef")
    assert len(summaries) == 2

    public = await service.get_public_report(report.id)
    assert public.report_id == report.id
    assert public.executive_summary_markdown == "Executive summary"
    assert public.metrics["Strategic Claim"] == 1.0
