"""API Router for Execution Views (BFF and Raw Data)."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, status

from backend.api.bff_transformer import ReportTransformer
from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_async_repository
from backend.exceptions import AppException, ResourceNotFoundError
from backend.logging_config import log_error
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
        if hasattr(execution, "model_dump"):
            raw_data = execution.model_dump()
        elif hasattr(execution, "dict"):
             raw_data = execution.dict()
        else:
            raw_data = execution

        # ---------------------------------------------------------
        # DYNAMIC STEP RESOLUTION (SSOT from Database)
        # ---------------------------------------------------------
        # ReportTransformer might not use steps list yet, but let's be consistent if we merge logic later.
        # Currently ReportView is different from AssessmentView.
        # If we use AssessmentTransformer here (for some reason?), we should pass steps.
        
        # Wait, views.py uses ReportTransformer for the "Report View" (Final Output).
        # Does ReportView need the step list? Not strictly. 
        # But if we were using AssessmentTransformer here...
        
        # Let's check imports. views.py imports ReportTransformer.
        # bff_transformer.py defines AssessmentTransformer AND ReportTransformer.
        # Does ReportTransformer need steps? 
        # Usually it just renders the report content.
        
        # However, for 'get_execution_view', if it returns ReportView, that's the "Result" screen.
        # It DOES contain 'steps' logic if we want to show the timeline there too?
        # ReportView in models/view.py might not have 'steps'.
        
        # Let's assume ReportTransformer doesn't need it yet, 
        # BUT if I ever switch this to return AssessmentView (Monitoring), I'll need it.
        # For now, I'll leave views.py alone UNLESS I see it using AssessmentTransformer.
        
        # Actually... let's check monitor.py again. monitor.py uses AssessmentTransformer.
        # views.py uses ReportTransformer.
        
        # The user request was "list only from database". 
        # This primarily affects the Monitoring Screen (AssessmentTransformer).
        # So monitor.py change is the critical one.
        
        # Resolve Scale (Simplified for now)
        valid_range = None

        view = transformer.transform(raw_data, valid_range=valid_range)
        return view


    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except Exception as e:
        error_code = "VIEW_TRANSFORMATION_FAILED"
        wrapped = AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e


@router.get(
    "/{execution_id}/raw",
    summary="Get Raw Execution Data",
    description="Returns complete raw execution data including agent and hook outputs.",
    response_model=dict[str, Any],
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

        raw_data = {
            "execution_id": execution.get("id"),
            "workflow_id": execution.get("workflow_id"),
            "status": execution.get("status"),
            "started_at": execution.get("started_at"),
            "completed_at": execution.get("completed_at"),
            "duration_seconds": None,
            "inputs": execution.get("inputs", {}),
            "results": execution.get("results", {}),
            "state": execution.get("state", {}),
            "user_id": execution.get("user_id"),
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

        return raw_data

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except Exception as e:
        error_code = "RAW_DATA_FETCH_FAILED"
        wrapped = AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e
