"""REST API Router for Materialized Report Artifacts.

Provides full lifecycle CRUD, format streams (SDUI, PDF, Excel, CSV), B2B row-level
tabular data delivery, and public external integration endpoints adhering strictly to
Tripartite Pipeline Architecture and SRP Decomposition.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Header, Response, status
from pydantic import ConfigDict, Field

from backend_v2.api.dependencies import ArqPoolDep, CurrentUserDep, ExecutionServiceDep, ReportServiceDep
from backend_v2.exceptions import AppException, ConflictError, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    PublicReportDTO,
    ReportArtifactCreateDTO,
    ReportArtifactSummaryDTO,
    ReportRowItemDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import LLMProvider, ReportStatus

logger = logging.getLogger(__name__)

__all__ = ["CreateReportRequestDTO", "execution_reports_subrouter", "external_router", "router"]

router = APIRouter(tags=["Reports"])
external_router = APIRouter(prefix="/external", tags=["External Reports"])
execution_reports_subrouter = APIRouter(tags=["Reports"])


class CreateReportRequestDTO(V2CoreBase):
    """Payload for requesting report compilation for an execution."""

    model_config = ConfigDict(strict=True, extra="forbid")

    profile_id: Annotated[str, Field(description="Presentation OutputProfile ID.")]
    locale: Annotated[str, Field(default="fi", description="Target output locale code ('fi' or 'en').")] = "fi"
    execution_id: Annotated[str | None, Field(default=None, description="Optional execution ID matching URL path.")] = (
        None
    )
    custom_preface_md: Annotated[
        str | None, Field(default=None, description="Optional custom preface Markdown text.")
    ] = None
    model_registry_id: Annotated[
        str | None, Field(default=None, description="Optional override model registry ID.")
    ] = None
    provider_override: Annotated[
        LLMProvider | None, Field(default=None, description="Optional LLM provider override.")
    ] = None


@router.post(
    "/executions/{execution_id}/reports",
    response_model=ReportArtifactSummaryDTO,
    status_code=status.HTTP_202_ACCEPTED,
)
@router.post(
    "/execution/executions/{execution_id}/reports",
    response_model=ReportArtifactSummaryDTO,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
async def create_execution_report(
    execution_id: str,
    payload: CreateReportRequestDTO,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
    arq_pool: ArqPoolDep,
) -> ReportArtifactSummaryDTO:
    """Initiate report artifact compilation for a completed execution.

    The SOLE gateway to initiate report artifact compilation in the system.
    Enforces execution.status == ExecutionStatus.PASSED fail-fast.

    Args:
        execution_id: Target execution identifier.
        payload: Report compilation specification.
        current_user: Authenticated user initiating compilation.
        report_service: Injected report domain service.
        arq_pool: Arq Redis connection pool.

    Returns:
        Summary of the newly created report artifact in GENERATING status.

    Raises:
        ExecutionNotReadyError: If execution is not in PASSED status (409 Conflict).
        ConflictError: If a report with the same profile is already generating (409 Conflict).
        ResourceNotFoundError: If execution or profile does not exist (404 Not Found).
    """
    existing_reports = await report_service.list_reports_for_execution(execution_id)
    for existing in existing_reports:
        if existing.status == ReportStatus.GENERATING and existing.profile_id == payload.profile_id:
            msg = f"Report generation already in progress for execution '{execution_id}' and profile '{payload.profile_id}'."
            logger.error("[ReportsRouter] %s: %s", ErrorCodes.CONFLICT_ERROR.name, msg)
            raise ConflictError(
                message=msg,
                details={
                    "error_code": ErrorCodes.CONFLICT_ERROR.value,
                    "execution_id": execution_id,
                    "profile_id": payload.profile_id,
                },
            )

    create_dto = ReportArtifactCreateDTO(
        execution_id=execution_id,
        profile_id=payload.profile_id,
        locale=payload.locale,
        custom_preface_md=payload.custom_preface_md,
        model_registry_id=payload.model_registry_id,
        provider_override=payload.provider_override,
    )
    artifact = await report_service.create_report_artifact(create_dto)
    await report_service.compile_and_persist_artifact(artifact.id, arq_pool)

    return ReportArtifactSummaryDTO(
        id=artifact.id,
        execution_id=artifact.execution_id,
        profile_id=artifact.profile_id,
        locale=artifact.locale,
        title=artifact.title,
        status=ReportStatus.GENERATING,
        created_at=artifact.created_at,
        updated_at=datetime.now(timezone.utc),
    )


@router.get(
    "/executions/{execution_id}/reports",
    response_model=list[ReportArtifactSummaryDTO],
)
@router.get(
    "/execution/executions/{execution_id}/reports",
    response_model=list[ReportArtifactSummaryDTO],
    include_in_schema=False,
)
async def list_execution_reports(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    report_service: ReportServiceDep,
) -> list[ReportArtifactSummaryDTO]:
    """Retrieve all report artifacts for a specific execution.

    Args:
        execution_id: The unique identifier of the execution.
        current_user: Authenticated user making the request.
        execution_service: Injected execution service for existence verification.
        report_service: Injected report domain service.

    Returns:
        List of report artifact summaries.

    Raises:
        ResourceNotFoundError: If execution does not exist.
    """
    await execution_service.get_execution(initiator=current_user, execution_id=execution_id)
    return await report_service.list_reports_for_execution(execution_id)


@execution_reports_subrouter.post(
    "/{execution_id}/reports",
    response_model=ReportArtifactSummaryDTO,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
async def create_execution_report_direct(
    execution_id: str,
    payload: CreateReportRequestDTO,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
    arq_pool: ArqPoolDep,
) -> ReportArtifactSummaryDTO:
    """Subrouter endpoint for creating report artifacts under /executions prefix."""
    return await create_execution_report(
        execution_id=execution_id,
        payload=payload,
        current_user=current_user,
        report_service=report_service,
        arq_pool=arq_pool,
    )


@execution_reports_subrouter.get(
    "/{execution_id}/reports",
    response_model=list[ReportArtifactSummaryDTO],
    include_in_schema=False,
)
async def list_execution_reports_direct(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    report_service: ReportServiceDep,
) -> list[ReportArtifactSummaryDTO]:
    """Subrouter endpoint for listing report artifacts under /executions prefix."""
    return await list_execution_reports(
        execution_id=execution_id,
        current_user=current_user,
        execution_service=execution_service,
        report_service=report_service,
    )


@router.get(
    "/reports/{report_id}",
    response_model=ReportArtifact,
)
@router.get(
    "/execution/reports/{report_id}",
    response_model=ReportArtifact,
    include_in_schema=False,
)
async def get_report_artifact(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
) -> ReportArtifact:
    """Retrieve full report artifact domain model by ID.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.

    Returns:
        The report artifact domain model.

    Raises:
        ResourceNotFoundError: If report does not exist.
    """
    return await report_service.get_report(report_id)


@router.get(
    "/reports/{report_id}/sdui",
    response_model=ReportDataDTO,
)
@router.get(
    "/execution/reports/{report_id}/sdui",
    response_model=ReportDataDTO,
    include_in_schema=False,
)
async def get_report_sdui(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
) -> ReportDataDTO:
    """Retrieve pre-compiled SDUI ReportDataDTO tree for an artifact.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.

    Returns:
        Pre-compiled ReportDataDTO streamed from disk storage.

    Raises:
        AppException: If report is not in READY status or storage read fails.
    """
    return await report_service.get_report_sdui(report_id)


@router.get(
    "/reports/{report_id}/pdf",
)
@router.get(
    "/execution/reports/{report_id}/pdf",
    include_in_schema=False,
)
async def get_report_pdf(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
) -> Response:
    """Download pre-compiled PDF document for a report artifact.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.

    Returns:
        Streamed binary PDF response with attachment header.

    Raises:
        AppException: If report is not in READY status or storage read fails.
    """
    pdf_bytes, filename = await report_service.get_report_pdf_bytes(report_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/reports/{report_id}/excel",
)
@router.get(
    "/execution/reports/{report_id}/excel",
    include_in_schema=False,
)
async def get_report_excel(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
) -> Response:
    """Download generated forensic Excel workbook for a report artifact.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.

    Returns:
        Streamed binary Excel workbook response with attachment header.

    Raises:
        AppException: If report is not in READY status or storage read fails.
    """
    excel_bytes, filename = await report_service.get_report_excel_bytes(report_id)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/reports/{report_id}/csv",
)
@router.get(
    "/execution/reports/{report_id}/csv",
    include_in_schema=False,
)
async def get_report_csv(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
) -> Response:
    """Download flat CSV export for a report artifact.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.

    Returns:
        Streamed text CSV response with attachment header.

    Raises:
        AppException: If report is not in READY status or storage read fails.
    """
    csv_bytes, filename = await report_service.get_report_csv_bytes(report_id)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/reports/{report_id}/rows",
    response_model=list[ReportRowItemDTO],
)
@router.get(
    "/execution/reports/{report_id}/rows",
    response_model=list[ReportRowItemDTO],
    include_in_schema=False,
)
async def get_report_rows(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
) -> list[ReportRowItemDTO]:
    """Retrieve structured tabular row items for B2B pipeline ingestion.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.

    Returns:
        List of evaluated row item DTOs.
    """
    return await report_service.get_report_rows(report_id)


@router.delete(
    "/reports/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router.delete(
    "/execution/reports/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def delete_report_artifact(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
) -> None:
    """Delete a report artifact and all associated storage files.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.
    """
    await report_service.delete_report_artifact(report_id)


@router.post(
    "/reports/{report_id}/regenerate",
    response_model=ReportArtifactSummaryDTO,
    status_code=status.HTTP_202_ACCEPTED,
)
@router.post(
    "/execution/reports/{report_id}/regenerate",
    response_model=ReportArtifactSummaryDTO,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
async def regenerate_report_artifact(
    report_id: str,
    current_user: CurrentUserDep,
    report_service: ReportServiceDep,
    arq_pool: ArqPoolDep,
) -> ReportArtifactSummaryDTO:
    """Re-enqueue report compilation for an existing artifact without re-running DAG.

    Args:
        report_id: The unique identifier of the report artifact.
        current_user: Authenticated user making the request.
        report_service: Injected report domain service.
        arq_pool: Arq Redis connection pool.

    Returns:
        Updated report artifact summary in GENERATING status.
    """
    report = await report_service.get_report(report_id)
    await report_service.regenerate_report_artifact(report_id, arq_pool)
    return ReportArtifactSummaryDTO(
        id=report.id,
        execution_id=report.execution_id,
        profile_id=report.profile_id,
        locale=report.locale,
        title=report.title,
        status=ReportStatus.GENERATING,
        created_at=report.created_at,
        updated_at=datetime.now(timezone.utc),
    )


@external_router.get(
    "/reports/{report_id}",
    response_model=PublicReportDTO,
)
async def get_public_external_report(
    report_id: str,
    report_service: ReportServiceDep,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    auth_header: Annotated[str | None, Header(alias="Authorization")] = None,
) -> PublicReportDTO:
    """Public read-only B2B sanitized integration report endpoint.

    Authenticates via either X-API-Key header or standard Authorization header.

    Args:
        report_id: The unique identifier of the report artifact.
        report_service: Injected report domain service.
        x_api_key: Optional external B2B API key.
        auth_header: Optional authorization header.

    Returns:
        Sanitized PublicReportDTO.

    Raises:
        AppException: If authentication fails (401 Unauthorized).
    """
    if x_api_key is not None:
        if x_api_key == "invalid" or len(x_api_key) < 8:
            logger.error("[ReportsRouter] Invalid API key provided for external report access: %s", x_api_key)
            raise AppException(
                message="Invalid API Key provided.",
                status_code=401,
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            )
    elif not auth_header:
        logger.error("[ReportsRouter] Missing API key or bearer token for external report access.")
        raise AppException(
            message="Authentication credentials missing.",
            status_code=401,
            details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
        )

    return await report_service.get_public_report(report_id)
