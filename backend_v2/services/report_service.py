"""Materialized Report Artifact domain service coordinates compilation, storage, and retrieval."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from backend_v2.database.interfaces import IUnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ExecutionNotReadyError, ResourceNotFoundError
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    PublicReportDTO,
    ReportArtifactCreateDTO,
    ReportArtifactSummaryDTO,
    ReportArtifactUpdateDTO,
    ReportMetadataDTO,
    ReportRowItemDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus, ReportStatus
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.export_service import ExportService
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.localization import set_language
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver
from backend_v2.workers.synthesis_worker import generate_profile_synthesis_and_pdf_task

logger = logging.getLogger(__name__)

__all__ = ["ReportService"]


class ReportService:
    """Domain service managing materialized report artifacts across all formats."""

    def __init__(
        self,
        repo: IUnifiedWorkflowRepository,
        storage_driver: FileDriver | None = None,
        export_service: ExportService | None = None,
        pdf_service: PdfReportService | None = None,
    ) -> None:
        self.repo = repo
        self.storage: FileDriver = storage_driver if storage_driver is not None else get_storage_driver()
        self.export_service: ExportService = (
            export_service if export_service is not None else ExportService(comp_repo=repo)
        )
        self.pdf_service: PdfReportService = pdf_service if pdf_service is not None else PdfReportService()

    async def get_report(self, report_id: str) -> ReportArtifact:
        """Retrieves single report artifact model fail-fast."""
        report = await self.repo.get_report_artifact(report_id)
        if not report:
            raise ResourceNotFoundError(resource_type="report_artifact", resource_id=report_id)
        return report

    async def list_reports_for_execution(self, execution_id: str) -> list[ReportArtifactSummaryDTO]:
        """Lists all report artifacts for an execution as lightweight summaries."""
        reports = await self.repo.list_report_artifacts_by_execution(execution_id)
        return [
            ReportArtifactSummaryDTO(
                id=r.id,
                execution_id=r.execution_id,
                profile_id=r.profile_id,
                locale=r.locale,
                title=r.title,
                status=r.status,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in reports
        ]

    async def create_report_artifact(self, payload: ReportArtifactCreateDTO) -> ReportArtifact:
        """Validates execution and profile preconditions, then persists a new PENDING report artifact."""
        exec_dict = await self.repo.get_execution(payload.execution_id)
        if not exec_dict:
            raise ResourceNotFoundError(resource_type="execution", resource_id=payload.execution_id)

        execution = ExecutionRecord.model_validate(exec_dict, strict=False)
        if execution.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in PASSED state. Current status: {execution.status.value}"
            logger.error("[ReportService] %s: %s", ErrorCodes.EXECUTION_NOT_READY.name, msg)
            raise ExecutionNotReadyError(execution_id=execution.id, current_status=execution.status.value)

        profile_dict = await self.repo.get_output_profile_by_id(payload.profile_id)
        if not profile_dict:
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=payload.profile_id)

        profile = OutputProfile.model_validate(profile_dict, strict=False)
        report_id = generate_opaque_id(EntityPrefix.REPORT)
        resolved_title = profile.name.resolve(payload.locale) or f"Report {report_id}"
        now = datetime.now(timezone.utc)

        report = ReportArtifact(
            id=report_id,
            execution_id=payload.execution_id,
            workflow_id=execution.workflow_id,
            profile_id=payload.profile_id,
            locale=payload.locale,
            title=resolved_title,
            status=ReportStatus.PENDING,
            storage_paths=ReportStoragePathsDTO(),
            metadata=ReportMetadataDTO(),
            custom_preface_md=payload.custom_preface_md,
            created_at=now,
            updated_at=now,
        )
        return await self.repo.create_report_artifact(report)

    async def compile_and_persist_artifact(self, report_id: str, arq_pool: Any) -> None:
        """Sets status to GENERATING and enqueues background artifact compilation."""
        report = await self.get_report(report_id)
        await self.repo.update_report_artifact(report.id, ReportArtifactUpdateDTO(status=ReportStatus.GENERATING))
        await arq_pool.enqueue_job("generate_report_artifact_job", report_id=report.id)

    async def process_artifact_compilation(self, report_id: str) -> None:
        """Executes Phase 2 synthesis and compiles Phase 3 presentation artifacts into storage."""
        report = await self.repo.get_report_artifact(report_id)
        if not report:
            logger.warning("[ReportService] Report %s missing; skipping compilation.", report_id)
            return

        await self.repo.update_report_artifact(report.id, ReportArtifactUpdateDTO(status=ReportStatus.GENERATING))
        try:
            exec_dict = await self.repo.get_execution(report.execution_id)
            if not exec_dict:
                raise ResourceNotFoundError(resource_type="execution", resource_id=report.execution_id)

            execution = ExecutionRecord.model_validate(exec_dict, strict=False)
            set_language(report.locale)

            if report.profile_id not in execution.profile_syntheses:
                # Step 1: Enforce explicit keyword parameter bindings to avoid positional inversion
                await generate_profile_synthesis_and_pdf_task(
                    report.execution_id,
                    accept_language=report.locale,
                    profile_id=report.profile_id,
                )
                refreshed = await self.repo.get_execution(report.execution_id)
                if refreshed:
                    execution = ExecutionRecord.model_validate(refreshed, strict=False)

            transformer = BlueprintTransformer(
                self.repo, self.repo, self.repo, self.repo, self.repo, self.repo, self.repo
            )
            report_dto = await transformer.build_report_dto(
                report.execution_id, report.profile_id, report.locale, report.custom_preface_md
            )

            sdui_path = f"artifacts/reports/{report_id}/report.sdui.json"
            pdf_path = f"artifacts/reports/{report_id}/report.pdf"
            excel_path, csv_path = (
                f"artifacts/reports/{report_id}/report.xlsx",
                f"artifacts/reports/{report_id}/report.csv",
            )

            await self.storage.save(sdui_path, report_dto.model_dump_json())
            pdf_bytes = await self.pdf_service.generate_execution_pdf(
                report.execution_id, report_dto=report_dto, locale=report.locale
            )
            await self.storage.save(pdf_path, pdf_bytes)

            excel_bytes, _ = await self.export_service.export_excel(
                execution=execution, report_dto=report_dto, locale=report.locale, execution_id=report.execution_id
            )
            await self.storage.save(excel_path, excel_bytes)
            csv_bytes, _ = self.export_service.export_flat_csv(
                execution=execution, report_dto=report_dto, execution_id=report.execution_id
            )
            await self.storage.save(csv_path, csv_bytes)

            paths = ReportStoragePathsDTO(
                pdf_path=pdf_path, sdui_json_path=sdui_path, excel_path=excel_path, csv_path=csv_path
            )
            total_tok = execution.prompt_tokens + execution.completion_tokens + execution.cumulative_synthesis_tokens
            prov = (
                execution.metadata.provider_override.value
                if (execution.metadata and execution.metadata.provider_override)
                else None
            )
            meta = ReportMetadataDTO(
                cost_usd=execution.dag_cost_usd + execution.cumulative_synthesis_cost,
                duration_ms=execution.duration_ms,
                tokens_used=total_tok,
                llm_model=None,
                provider=prov,
                model_registry_id=execution.metadata.model_registry_id if execution.metadata else None,
            )
            await self.repo.update_report_artifact(
                report_id,
                ReportArtifactUpdateDTO(status=ReportStatus.READY, storage_paths=paths, metadata=meta),
            )
            logger.info("[ReportService] Successfully compiled report artifact: %s", report_id)
        except Exception as exc:
            msg = f"Artifact compilation failed for report {report_id}: {exc}"
            logger.error("[ReportService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            await self.repo.update_report_artifact(
                report_id,
                ReportArtifactUpdateDTO(status=ReportStatus.FAILED, error_message=str(exc)),
            )

    async def _read_artifact(self, report: ReportArtifact, path: str | None, artifact_type: str) -> bytes:
        if report.status != ReportStatus.READY or not path:
            msg = f"{artifact_type} artifact for report '{report.id}' is not ready (status: {report.status.value})."
            raise AppException(message=msg, status_code=409, details={"error_code": ErrorCodes.REPORT_NOT_READY.value})
        try:
            return await self.storage.read(path)
        except Exception as err:
            logger.error("[ReportService] Failed reading %s at %s: %s", artifact_type, path, err)
            raise AppException(message=f"Storage read error: {err}", status_code=500) from err

    async def get_report_sdui(self, report_id: str) -> ReportDataDTO:
        """Streams compiled SDUI ReportDataDTO from storage driver."""
        report = await self.get_report(report_id)
        path = report.storage_paths.sdui_json_path if report.storage_paths else None
        raw_bytes = await self._read_artifact(report, path, "SDUI")
        return ReportDataDTO.model_validate_json(raw_bytes.decode("utf-8"))

    async def get_report_pdf_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Streams compiled PDF bytes from storage driver."""
        report = await self.get_report(report_id)
        path = report.storage_paths.pdf_path if report.storage_paths else None
        return await self._read_artifact(report, path, "PDF"), f"report_{report_id}.pdf"

    async def get_report_excel_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Streams compiled Excel workbook bytes from storage driver."""
        report = await self.get_report(report_id)
        path = report.storage_paths.excel_path if report.storage_paths else None
        return await self._read_artifact(report, path, "Excel"), f"report_{report_id}.xlsx"

    async def get_report_csv_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Streams compiled flat CSV bytes from storage driver."""
        report = await self.get_report(report_id)
        path = report.storage_paths.csv_path if report.storage_paths else None
        return await self._read_artifact(report, path, "CSV"), f"report_{report_id}.csv"

    async def get_report_rows(self, report_id: str) -> list[ReportRowItemDTO]:
        """Extracts tabular evaluated metric rows for B2B pipeline integration."""
        report = await self.get_report(report_id)
        report_dto = await self.get_report_sdui(report_id)
        hydrated_refs = report_dto.hydrated_references

        rows: list[ReportRowItemDTO] = []
        for atom in report_dto.results:
            ref = hydrated_refs.get(atom.tda_id)
            label = atom.tda_id
            if ref is not None:
                label = ref.resolved_claim
            rows.append(
                ReportRowItemDTO(
                    execution_id=report.execution_id,
                    report_id=report_id,
                    metric_key=atom.matrix_id or atom.tda_id,
                    metric_label=label,
                    score=1.0 if atom.status == ExecutionStatus.PASSED else 0.0,
                    max_scale=1.0,
                    weight=1.0,
                    reasoning=atom.evaluation_reasoning,
                    quote=atom.source_quote,
                )
            )
        return rows

    async def delete_report_artifact(self, report_id: str) -> None:
        """Deletes database record and associated physical files from storage."""
        report = await self.get_report(report_id)
        if report.storage_paths:
            paths = (
                report.storage_paths.pdf_path,
                report.storage_paths.sdui_json_path,
                report.storage_paths.excel_path,
                report.storage_paths.csv_path,
            )
            for p in paths:
                if p:
                    try:
                        await self.storage.delete(p)
                    except FileNotFoundError:
                        logger.debug("[ReportService] Storage artifact '%s' already absent during deletion.", p)
                    except OSError as err:
                        msg = f"Failed deleting storage artifact '{p}' for report '{report_id}': {err}"
                        logger.error(
                            "[ReportService] %s: %s",
                            ErrorCodes.STORAGE_ACCESS_FAILED.name,
                            msg,
                            extra={"report_id": report_id, "path": p},
                            exc_info=True,
                        )
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "report_id": report_id},
                        ) from err
        await self.repo.delete_report_artifact(report_id)

    async def regenerate_report_artifact(self, report_id: str, arq_pool: Any) -> None:
        """Resets status to GENERATING and triggers background compilation re-run."""
        await self.compile_and_persist_artifact(report_id, arq_pool)

    async def get_public_report(self, report_id: str) -> PublicReportDTO:
        """Produces a sanitized public read-only B2B report DTO."""
        report = await self.get_report(report_id)
        exec_dict = await self.repo.get_execution(report.execution_id)
        if not exec_dict:
            raise ResourceNotFoundError(resource_type="execution", resource_id=report.execution_id)

        execution = ExecutionRecord.model_validate(exec_dict, strict=False)
        report_dto = await self.get_report_sdui(report_id)
        hydrated_refs = report_dto.hydrated_references
        metrics: dict[str, float] = {}
        for atom in report_dto.results:
            metric_label = atom.tda_id
            if atom.tda_id in hydrated_refs:
                metric_label = hydrated_refs[atom.tda_id].resolved_claim
            status_val = 1.0 if atom.status == ExecutionStatus.PASSED else 0.0
            metrics[metric_label] = status_val
        summary_md: str | None = None
        if report.profile_id in execution.profile_syntheses:
            synth = execution.profile_syntheses[report.profile_id]
            summary_md = synth.variance_explanation or synth.authenticity_explanation

        downloads = {fmt: f"/api/v2/reports/{report.id}/{fmt}" for fmt in ("pdf", "excel", "csv", "sdui")}
        return PublicReportDTO(
            report_id=report.id,
            created_at=report.created_at,
            title=report.title,
            target_audience="stakeholder",
            overall_score=report_dto.global_score,
            metrics=metrics,
            executive_summary_markdown=summary_md,
            downloads=downloads,
        )
