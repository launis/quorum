"""Unit test suite for ReportService verifying full report artifact lifecycle.

Enforces Tripartite Phase Isolation, Four-Tier Pydantic V2 Invariants, and failure containment.
"""

from unittest.mock import AsyncMock, MagicMock

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
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType, ReportStatus, VisualIntent
from backend_v2.services.report_service import ReportService


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
    repo = AsyncMock()
    repo.get_execution.return_value = _create_dummy_execution().model_dump(mode="json")
    repo.get_output_profile_by_id.return_value = _create_dummy_profile().model_dump(mode="json")
    repo.create_report_artifact.side_effect = lambda rep: rep

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
    repo.create_report_artifact.assert_called_once()


@pytest.mark.asyncio
async def test_create_report_artifact_entry_execution_not_found() -> None:
    repo = AsyncMock()
    repo.get_execution.return_value = None
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_missing", profile_id="prf_1")
    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(payload)


@pytest.mark.asyncio
async def test_create_report_artifact_entry_execution_not_passed() -> None:
    repo = AsyncMock()
    repo.get_execution.return_value = _create_dummy_execution(status=ExecutionStatus.RUNNING).model_dump(mode="json")
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_1234567890abcdef", profile_id="prf_1")
    with pytest.raises(AppException) as exc_info:
        await service.create_report_artifact(payload)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_create_report_artifact_entry_profile_not_found() -> None:
    repo = AsyncMock()
    repo.get_execution.return_value = _create_dummy_execution().model_dump(mode="json")
    repo.get_output_profile_by_id.return_value = None
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    payload = ReportArtifactCreateDTO(execution_id="exe_1234567890abcdef", profile_id="prf_missing")
    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(payload)


@pytest.mark.asyncio
async def test_compile_and_persist_artifact() -> None:
    repo = AsyncMock()
    report = _create_dummy_report()
    repo.get_report_artifact.return_value = report
    arq_pool = AsyncMock()

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    await service.compile_and_persist_artifact(report.id, arq_pool)

    repo.update_report_artifact.assert_called_once()
    arq_pool.enqueue_job.assert_called_once_with("generate_report_artifact_job", report_id=report.id)


@pytest.mark.asyncio
async def test_process_artifact_compilation_success(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = AsyncMock()
    report = _create_dummy_report()
    repo.get_report_artifact.return_value = report
    repo.get_execution.return_value = _create_dummy_execution().model_dump(mode="json")

    storage = AsyncMock()
    storage.save.side_effect = lambda path, data: path

    export_service = AsyncMock()
    export_service.export_excel.return_value = (b"excel_bytes", "report.xlsx")
    export_service.export_flat_csv = MagicMock(return_value=(b"csv_bytes", "report.csv"))

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
    # Status updated to GENERATING then READY
    assert repo.update_report_artifact.call_count == 2
    final_call_args = repo.update_report_artifact.call_args_list[-1]
    assert final_call_args[0][1].status == ReportStatus.READY


@pytest.mark.asyncio
async def test_process_artifact_compilation_failure_isolation() -> None:
    repo = AsyncMock()
    report = _create_dummy_report()
    repo.get_report_artifact.return_value = report
    # Simulate execution fetch failure
    repo.get_execution.return_value = None

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    await service.process_artifact_compilation(report.id)

    # Invariant: Failure must set ReportArtifact to FAILED without crashing or mutating ExecutionRecord
    final_update = repo.update_report_artifact.call_args_list[-1][0][1]
    assert final_update.status == ReportStatus.FAILED
    assert final_update.error_message is not None


@pytest.mark.asyncio
async def test_get_report_sdui_and_streams() -> None:
    repo = AsyncMock()
    report = _create_dummy_report(status=ReportStatus.READY)
    repo.get_report_artifact.return_value = report

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
    repo = AsyncMock()
    report = _create_dummy_report(status=ReportStatus.READY)
    repo.get_report_artifact.return_value = report
    repo.get_execution.return_value = _create_dummy_execution().model_dump(mode="json")
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
    repo = AsyncMock()
    report = _create_dummy_report()
    repo.get_report_artifact.return_value = report
    storage = AsyncMock()

    service = ReportService(repo=repo, storage_driver=storage)
    await service.delete_report_artifact(report.id)

    assert storage.delete.call_count == 4
    repo.delete_report_artifact.assert_called_once_with(report.id)


@pytest.mark.asyncio
async def test_list_and_public_reports() -> None:
    repo = AsyncMock()
    report = _create_dummy_report(status=ReportStatus.READY)
    repo.get_report_artifact.return_value = report
    repo.list_report_artifacts_by_execution.return_value = [report]
    repo.get_execution.return_value = _create_dummy_execution().model_dump(mode="json")
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
    repo = AsyncMock()
    report = _create_dummy_report()
    repo.get_report_artifact.return_value = report
    storage = AsyncMock()
    storage.delete.side_effect = OSError("Disk write protected")

    service = ReportService(repo=repo, storage_driver=storage)
    with pytest.raises(AppException) as exc_info:
        await service.delete_report_artifact(report.id)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_regenerate_report_artifact() -> None:
    """Verify regenerate_report_artifact enqueues compilation job."""
    repo = AsyncMock()
    report = _create_dummy_report()
    repo.get_report_artifact.return_value = report
    arq = AsyncMock()

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    await service.regenerate_report_artifact(report.id, arq)
    arq.enqueue_job.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_report_artifact_workflow_id_mismatch() -> None:
    """Verify create_report_artifact fails fast when profile does not belong to execution workflow."""
    repo = AsyncMock()
    repo.get_execution.return_value = _create_dummy_execution().model_dump(mode="json")
    mismatched_profile = _create_dummy_profile().model_copy(update={"workflow_id": "wor_other_workflow_123"})
    repo.get_output_profile_by_id.return_value = mismatched_profile.model_dump(mode="json")

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
    repo = AsyncMock()
    execution = _create_dummy_execution()
    repo.get_execution.return_value = execution.model_dump(mode="json")
    existing_report = _create_dummy_report()
    repo.list_report_artifacts_by_execution.return_value = [existing_report]

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_or_create_default_artifact(
        execution_id=execution.id,
        profile_id="prf_1234567890abcdef",
        locale="fi",
    )

    assert result.id == existing_report.id
    repo.create_report_artifact.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_creates_when_none() -> None:
    """Verify get_or_create_default_artifact creates a new report artifact using execution default profile."""
    repo = AsyncMock()
    execution = _create_dummy_execution()
    execution = execution.model_copy(update={"output_profile_id": "prf_1234567890abcdef"})
    repo.get_execution.return_value = execution.model_dump(mode="json")
    repo.list_report_artifacts_by_execution.return_value = []
    repo.get_output_profile_by_id.return_value = _create_dummy_profile().model_dump(mode="json")
    repo.create_report_artifact.side_effect = lambda rep: rep

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    result = await service.get_or_create_default_artifact(
        execution_id=execution.id,
    )

    assert result.execution_id == execution.id
    assert result.profile_id == "prf_1234567890abcdef"
    assert result.locale == "fi"
    repo.create_report_artifact.assert_called_once()


@pytest.mark.asyncio
async def test_process_artifact_compilation_syncs_execution_record(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify compilation updates ExecutionRecord.pdf_report_path and sys_render step state."""
    repo = AsyncMock()
    report = _create_dummy_report()
    repo.get_report_artifact.return_value = report
    execution = _create_dummy_execution()
    repo.get_execution.return_value = execution.model_dump(mode="json")

    storage = AsyncMock()
    storage.save.side_effect = lambda path, data: path

    export_service = AsyncMock()
    export_service.export_excel.return_value = (b"excel_bytes", "report.xlsx")
    export_service.export_flat_csv = MagicMock(return_value=(b"csv_bytes", "report.csv"))

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

    repo.update_execution.assert_called_once()
    update_dto = repo.update_execution.call_args[0][1]
    assert update_dto.pdf_report_path == f"artifacts/reports/{report.id}/report.pdf"
    assert update_dto.step_states is not None
    assert f"sys_render_{report.profile_id}" in update_dto.step_states
    assert update_dto.step_states[f"sys_render_{report.profile_id}"].status == ExecutionStatus.PASSED
    assert update_dto.step_states[f"sys_render_{report.profile_id}"].progress == 100


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_execution_not_found() -> None:
    """Verify get_or_create_default_artifact raises ResourceNotFoundError if execution does not exist."""
    repo = AsyncMock()
    repo.get_execution.return_value = None
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.get_or_create_default_artifact("exe_nonexistent")


@pytest.mark.asyncio
async def test_get_or_create_default_artifact_workflow_default_and_fallback() -> None:
    """Verify get_or_create_default_artifact resolves workflow default_profile_id and fallback profiles."""
    repo = AsyncMock()
    execution = _create_dummy_execution()
    repo.get_execution.return_value = execution.model_dump(mode="json")
    repo.list_report_artifacts_by_execution.return_value = []

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
    repo.get_workflow.return_value = workflow.model_dump(mode="json")
    default_profile = _create_dummy_profile(profile_id="prf_0000000000000001")
    repo.get_output_profile_by_id.return_value = default_profile.model_dump(mode="json")
    repo.create_report_artifact.side_effect = lambda rep: rep

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    res1 = await service.get_or_create_default_artifact(execution.id)
    assert res1.profile_id == "prf_0000000000000001"

    # Case 2: Workflow default_profile_id is None, falls back to first matching profile
    workflow_no_default = workflow.model_copy(update={"default_profile_id": None})
    repo.get_workflow.return_value = workflow_no_default.model_dump(mode="json")
    fallback_profile = _create_dummy_profile(profile_id="prf_0000000000000002")
    repo.get_all_output_profiles.return_value = [fallback_profile]
    repo.get_output_profile_by_id.return_value = fallback_profile.model_dump(mode="json")

    res2 = await service.get_or_create_default_artifact(execution.id)
    assert res2.profile_id == "prf_0000000000000002"

    # Case 3: No matching profiles raises ResourceNotFoundError
    repo.get_all_output_profiles.return_value = []
    with pytest.raises(ResourceNotFoundError):
        await service.get_or_create_default_artifact(execution.id)


@pytest.mark.asyncio
async def test_process_artifact_compilation_missing_report_raises() -> None:
    """Verify process_artifact_compilation raises ResourceNotFoundError if report does not exist."""
    repo = AsyncMock()
    repo.get_report_artifact.return_value = None
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.process_artifact_compilation("rep_missing")


@pytest.mark.asyncio
async def test_read_artifact_failures() -> None:
    """Verify _read_artifact raises AppException when not ready or storage read fails."""
    repo = AsyncMock()
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
    repo = AsyncMock()
    report = _create_dummy_report(status=ReportStatus.READY)
    repo.get_report_artifact.return_value = report
    repo.get_execution.return_value = None

    service = ReportService(repo=repo, storage_driver=AsyncMock())
    with pytest.raises(ResourceNotFoundError):
        await service.get_public_report(report.id)
