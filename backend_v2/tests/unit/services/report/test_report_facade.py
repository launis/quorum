"""Unit tests for the ReportService package aggregator facade and Phase 4 cutover contracts."""

import ast
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    ExecutionNotReadyError,
    ResourceNotFoundError,
)
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import (
    ExecutionMetadata,
    ExecutionRecord,
    ExecutionStep,
    FrozenContext,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
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
from backend_v2.models.enums import (
    ExecutionStatus,
    LaxSDUIComponentType,
    LLMProvider,
    ReportStatus,
    VisualIntent,
)
from backend_v2.services import blueprint
from backend_v2.services.report import (
    ReportCompilationService,
    ReportFormatReaderService,
    ReportLifecycleService,
    ReportService,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from scripts._ast_guardrails import GuardrailSeverity, scan_files_for_guardrails


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
        metadata=ExecutionMetadata(
            provider_override=LLMProvider.VERTEX_AI,
            model_registry_id="cfg_model_registry_01",
        ),
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


def test_zero_legacy_report_service_imports() -> None:
    """Contract: Codebase-wide check for legacy report_service module finds 0 remaining imports."""
    retired_module = "backend_v2.services." + "report_service"
    retired_file = Path("backend_v2/services/" + "report_service.py")
    assert not retired_file.exists(), f"External proxy {retired_file} must be deleted."

    offending_files: list[str] = []
    for py_file in Path("backend_v2").rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        if retired_module in source:
            offending_files.append(str(py_file))
            continue
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == retired_module or alias.name.endswith(".report_service"):
                        offending_files.append(str(py_file))
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module == retired_module or node.module.endswith(".report_service"):
                    offending_files.append(str(py_file))

    assert offending_files == [], f"Found legacy report_service imports in: {offending_files}"


@pytest.mark.asyncio
async def test_package_facade_instantiation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Contract: Import ReportService from backend_v2.services.report and verify sub-service routing."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution())
    await repo.save_output_profile(_create_dummy_profile())

    sdui_dto = _create_dummy_report_data_dto()
    sdui_bytes = sdui_dto.model_dump_json().encode("utf-8")

    storage = AsyncMock()
    storage.save.side_effect = lambda path, data: path
    storage.delete = AsyncMock()

    export_service = AsyncMock()
    export_service.export_excel.return_value = ExportPayloadDTO(
        content_bytes=b"EXCEL_BYTES", filename="exec.xlsx", mime_type="app/xlsx"
    )
    export_service.export_flat_csv.return_value = ExportPayloadDTO(
        content_bytes=b"CSV_BYTES", filename="exec.csv", mime_type="text/csv"
    )
    pdf_service = AsyncMock()
    pdf_service.generate_execution_pdf.return_value = b"%PDF-1.4"

    monkeypatch.setattr(
        blueprint.BlueprintTransformer, "build_report_dto", AsyncMock(return_value=sdui_dto)
    )

    service = ReportService(
        repo=repo,
        storage_driver=storage,
        export_service=export_service,
        pdf_service=pdf_service,
        synthesis_runner=AsyncMock(),
    )

    assert isinstance(service._lifecycle, ReportLifecycleService)
    assert isinstance(service._compilation, ReportCompilationService)
    assert isinstance(service._format_reader, ReportFormatReaderService)

    # 1. create_report_artifact, get_report, list_reports_for_execution, get_or_create_default_artifact
    created = await service.create_report_artifact(
        ReportArtifactCreateDTO(
            execution_id="exe_1234567890abcdef",
            profile_id="prf_1234567890abcdef",
            locale="fi",
        )
    )
    fetched = await service.get_report(created.id)
    assert fetched.id == created.id

    summaries = await service.list_reports_for_execution("exe_1234567890abcdef")
    assert len(summaries) == 1
    assert summaries[0].id == created.id

    default_art = await service.get_or_create_default_artifact(
        "exe_1234567890abcdef", "prf_1234567890abcdef", "fi"
    )
    assert default_art.id == created.id

    # 2. compile_and_persist_artifact & process_artifact_compilation
    mock_arq = AsyncMock()
    await service.compile_and_persist_artifact(created.id, mock_arq, force_resynthesis=False)
    mock_arq.enqueue_job.assert_called_once()

    await service.process_artifact_compilation(created.id, force_resynthesis=False)
    ready_report = await service.get_report(created.id)
    assert ready_report.status == ReportStatus.READY

    # 3. Format readers: _read_artifact, get_report_sdui, pdf, excel, csv, rows, public
    storage.read.return_value = sdui_bytes
    raw_bytes = await service._read_artifact(ready_report, ready_report.storage_paths.sdui_json_path, "SDUI JSON")
    assert raw_bytes == sdui_bytes

    sdui_out = await service.get_report_sdui(created.id)
    assert sdui_out.execution_id == "exe_1234567890abcdef"

    rows = await service.get_report_rows(created.id)
    assert len(rows) == 1
    assert rows[0].metric_key == "blk_0123456789abcdef"

    public_dto = await service.get_public_report(created.id)
    assert public_dto.report_id == created.id

    storage.read.return_value = b"%PDF-1.4"
    pdf_bytes, pdf_name = await service.get_report_pdf_bytes(created.id)
    assert pdf_bytes == b"%PDF-1.4"
    assert pdf_name.endswith(".pdf")

    storage.read.return_value = b"EXCEL_BYTES"
    excel_bytes, excel_name = await service.get_report_excel_bytes(created.id)
    assert excel_bytes == b"EXCEL_BYTES"
    assert excel_name.endswith(".xlsx")

    storage.read.return_value = b"CSV_BYTES"
    csv_bytes, csv_name = await service.get_report_csv_bytes(created.id)
    assert csv_bytes == b"CSV_BYTES"
    assert csv_name.endswith(".csv")

    # 4. _dlq_log_absent_storage_artifact, regenerate_report_artifact, _dispatch_report_compilation_dlq, delete
    service._dlq_log_absent_storage_artifact("artifacts/missing.pdf")
    await service.regenerate_report_artifact(created.id, mock_arq)
    await service._dispatch_report_compilation_dlq(created.id, RuntimeError("Simulated DLQ error"))
    failed_report = await service.get_report(created.id)
    assert failed_report.status == ReportStatus.FAILED

    await service.delete_report_artifact(created.id)
    with pytest.raises(ResourceNotFoundError):
        await service.get_report(created.id)


@pytest.mark.asyncio
async def test_package_facade_negative_not_found() -> None:
    """Negative test: get_report and create_report_artifact raise ResourceNotFoundError on unknown IDs."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ReportService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ResourceNotFoundError):
        await service.get_report("rep_0000000000000000")

    with pytest.raises(ResourceNotFoundError):
        await service.create_report_artifact(
            ReportArtifactCreateDTO(
                execution_id="exe_0000000000000000",
                profile_id="prf_1234567890abcdef",
                locale="fi",
            )
        )


@pytest.mark.asyncio
async def test_package_facade_negative_not_ready() -> None:
    """Negative test: create_report_artifact on RUNNING execution and get_report_sdui on PENDING report fail fast."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_execution(_create_dummy_execution(status=ExecutionStatus.RUNNING))
    await repo.create_report_artifact(_create_dummy_report(status=ReportStatus.PENDING))

    service = ReportService(repo=repo, storage_driver=AsyncMock())

    with pytest.raises(ExecutionNotReadyError):
        await service.create_report_artifact(
            ReportArtifactCreateDTO(
                execution_id="exe_1234567890abcdef",
                profile_id="prf_1234567890abcdef",
                locale="fi",
            )
        )

    with pytest.raises(AppException) as exc_info:
        await service.get_report_sdui("rep_1234567890abcdef")
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.REPORT_NOT_READY.value


def test_qgr017_bans_legacy_report_service_import(tmp_path: Path) -> None:
    """Negative test: QGR017 triggers FATAL violation when importing retired report_service module."""
    bad_file = tmp_path / "consumer.py"
    legacy_mod = "backend_v2.services." + "report_service"
    bad_file.write_text(f"from {legacy_mod} import ReportService\n", encoding="utf-8")

    violations, is_success = scan_files_for_guardrails([bad_file], strict=True)
    qgr017 = [v for v in violations if v.rule_code == "QGR017"]
    assert not is_success
    assert len(qgr017) == 1
    assert qgr017[0].severity == GuardrailSeverity.FATAL
