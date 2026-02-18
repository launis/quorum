"""API Router for Execution Views (BFF and Raw Data)."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, status

from backend.api.bff_transformer import ReportTransformer
from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_async_repository
from backend.exceptions import AppException, ResourceNotFoundError
from backend.logging_config import log_error
from backend.models.dtos.execution import ExecutionRawResponse
from backend.models.view import ReportView
from backend.schemas.error import APIError
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get(
    "/{execution_id}/view",
    response_model=ReportView,
    summary="Get Execution View",
    description="Returns a pre-processed UI view of the execution results (BFF Pattern).",
    responses={
        404: {"model": APIError, "description": "Execution not found"},
        500: {"model": APIError, "description": "Transformation failed"},
    },
)
async def get_execution_view(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    accept_language: Annotated[str | None, Header()] = "en",
):
    """BFF Endpoint: Transforms raw execution data into a ReportView."""
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Transform logic
        transformer = ReportTransformer(language=accept_language or "en")
        
        if accept_language:
            transformer.language = accept_language

        # Resolve Scale (Simplified for now)
        valid_range = None
        # if execution... (logic to extract scale)

        # STRICT TYPING MANDATE (Part 2.4): Pass Pydantic Model, NOT dict.
        # ReportTransformer now enforces isinstance(ExecutionRecord).
        view = transformer.transform(execution, valid_range=valid_range)
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
        error_code = "VIEW_TRANSFORMATION_FAILED"
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
        transformer = ReportTransformer(language="en")
        
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
