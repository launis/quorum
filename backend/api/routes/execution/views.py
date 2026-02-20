"""API Router for Execution Views (BFF and Raw Data)."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Response, status
from fastapi.responses import JSONResponse

from backend.api.transformers.report_transformer import ReportTransformer
from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_async_repository
from backend.exceptions import AppException, ResourceNotFoundError, ErrorCodes
from backend.logging_config import log_error
from backend.models.dtos.execution import ExecutionRawResponse
from backend.models.dtos.report import XAIFlatReportDTO
from backend.models.view.sdui import ReportView
from backend.schemas.error import APIError
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get(
    "/{execution_id}/view",
    response_model=ReportView,
    summary="Get Execution Report View (BFF)",
    description="Returns the SDUI-optimized view model for the Report UI.",
    responses={
        404: {"model": APIError, "description": "Execution not found"},
        409: {"model": APIError, "description": "Report not ready"},
        500: {"model": APIError, "description": "Transformation failed"},
    },
)
async def get_execution_view(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    accept_language: Annotated[str | None, Header()] = "en",
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """BFF Endpoint: Transforms raw execution data into a ReportView."""
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Transform logic
        transformer = ReportTransformer() # Config language if needed
        
        # STRICT TYPING MANDATE: Pass Pydantic Model.
        view = transformer.transform(execution)
        return view

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND}
        ) from e
    except AppException:
        raise
    except Exception as e:
        error_code = ErrorCodes.REPORT_GENERATION_FAILED
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.get(
    "/{execution_id}/flat",
    response_model=XAIFlatReportDTO,
    summary="Get Flat Report (Integration)",
    description="Returns the machine-readable flat report (XAIFlatReportDTO).",
    responses={
        404: {"model": APIError, "description": "Execution or Report not found"},
    },
)
async def get_flat_report(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Integration Endpoint: Returns the persisted flat report."""
    try:
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Extract from step_xai
        xai_data = execution.context_variables.get("step_xai")
        if not xai_data or "flat_report" not in xai_data:
             raise AppException(
                message="Flat report not found in execution state.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": ErrorCodes.REPORT_NOT_READY}
            )
            
        return XAIFlatReportDTO(**xai_data["flat_report"])

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND}
        ) from e
    except AppException:
        raise
    except Exception as e:
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.get(
    "/{execution_id}/pdf",
    summary="Download PDF Report",
    description="Generates and returns the PDF report.",
    response_class=Response,
    responses={
        404: {"model": APIError, "description": "Execution not found"},
    },
)
async def get_pdf_report(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Generates PDF using PdfReportService."""
    try:
        # Check existence first
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Use the standard PDF Service
        from backend.services.pdf_generator import PdfReportService
        
        # We instantiate with repository. Progress service is optional (None).
        service = PdfReportService(repository=repository)
        
        pdf_bytes = await service.generate_execution_pdf(execution_id)
        
        if not pdf_bytes:
             raise AppException(
                message="PDF generation failed (empty output).",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.PDF_GENERATION_FAILED}
            )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{execution_id}.pdf"}
        )

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND}
        ) from e
    except AppException:
        raise
    except Exception as e:
        error_code = ErrorCodes.PDF_GENERATION_FAILED
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.get(
    "/{execution_id}/json",
    summary="Export Execution JSON",
    description="Returns the execution report as a raw JSON dump (Common Intermediate Representation).",
    response_model=ReportView,
    responses={
        404: {"model": APIError, "description": "Execution not found"},
        500: {"model": APIError, "description": "Export failed"},
    },
)
async def get_execution_json_export(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
):
    """Exports the ReportView as a JSON dictionary (CIR)."""
    try:
        # 1. Fetch Execution (Fail Fast)
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # 2. Transform to View Model
        # Use default language (en) or assume neutrality for machine export
        # Note: ReportTransformer constructor does not take arguments in current impl using @staticmethod,
        # but if it did (line 204 in original was `ReportTransformer(language="en")`), we adjust.
        # My impl assumes static transform.
        transformer = ReportTransformer()
        
        # STRICT TYPING MANDATE (Part 2.4): Pass Pydantic Model, NOT dict.
        view = transformer.transform(execution)

        # 3. Return View Model
        # FastAPI handles serialization (including dates/enum values) based on response_model
        return view

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except AppException:
        raise
    except Exception as e:
        error_code = "EXPORT_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@router.get(
    "/{execution_id}/raw",
    summary="Get Raw Execution Data",
    description="Returns complete raw execution data including agent and hook outputs.",
    response_model=ExecutionRawResponse,
)
async def get_execution_raw(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get complete raw execution data for debugging/reporting."""
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Normalize record to dict
        if hasattr(execution, "model_dump"):
             execution_dict = execution.model_dump()
        else:
             execution_dict = execution

        raw_data = {
            "execution_id": execution_dict.get("id"),
            "workflow_id": execution_dict.get("workflow_id"),
            "status": execution_dict.get("status"),
            "started_at": execution_dict.get("started_at"),
            "completed_at": execution_dict.get("completed_at"),
            "duration_seconds": None,
            "inputs": execution_dict.get("inputs", {}),
            "results": execution_dict.get("results", {}),
            "state": execution_dict.get("state", {}),
            "user_id": execution_dict.get("user_id"),
        }

        if raw_data["started_at"] and raw_data["completed_at"]:
            try:
                from datetime import datetime
                # Handle inconsistent types (str vs datetime)
                start_raw = raw_data["started_at"]
                end_raw = raw_data["completed_at"]

                start = (
                    datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
                    if isinstance(start_raw, str)
                    else start_raw
                )
                end = (
                    datetime.fromisoformat(str(end_raw).replace("Z", "+00:00"))
                    if isinstance(end_raw, str)
                    else end_raw
                )

                if start and end:
                    raw_data["duration_seconds"] = (end - start).total_seconds()
            except Exception:
                pass

        results = raw_data["results"]
        raw_data["agent_outputs"] = {
            key: results.get(key)
            for key in [
                "step_guard", "step_analyst", "step_profiler", "step_logician",
                "step_falsifier", "step_causal", "step_detector", "step_overseer",
                "step_archivist", "step_judge", "step_coach", "step_xai"
            ]
            if results.get(key)
        }

        raw_data["hook_outputs"] = results.get("aux_data", {})
        raw_data["xai_report"] = results.get("xai_report_formatted", "")

        return ExecutionRawResponse(**raw_data)

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except Exception as e:
        error_code = "RAW_DATA_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e
