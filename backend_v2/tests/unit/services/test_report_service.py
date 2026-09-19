"""Unit test suite for ReportService verifying full report artifact lifecycle.

Enforces Tripartite Phase Isolation, Four-Tier Pydantic V2 Invariants, and failure containment.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.report_artifact import ReportArtifact
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
        profile_syntheses={},
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
