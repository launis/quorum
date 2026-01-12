"""API Router for Orchestration and Workflow Execution.

This module provides endpoints for creating workflows, starting executions,
monitoring progress, and retrieving results.
"""

import logging
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Form,
    HTTPException,
    Path,
    Request,
    UploadFile,
)
from fastapi import (
    Query as APIQuery,
)
from pydantic import BaseModel, Field
from starlette.datastructures import UploadFile as StarletteUploadFile

from backend.dependencies import CurrentUserDep, EngineDep
from backend.models.auth import UserRole  # Required for role check
from backend.models.state import WorkflowState  # Required for migration/hydration logic
from backend.schemas.execution import ExecutionRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Orchestration"])


# --- Request Models ---


class ExecutionWorkflowCreateRequest(BaseModel):
    """Payload for creating a new workflow definition.

    Attributes:
        name (str): Human-readable name.
        steps (list[dict]): List of step configurations.
    """

    name: Annotated[str, Field(description="The unique, human-readable name for the new workflow.")]
    steps: Annotated[
        list[dict[str, Any]], Field(description="A sequential list of step configurations defining the workflow logic.")
    ]


class WorkflowExecutionRequest(BaseModel):
    """Payload for starting a new execution.

    Attributes:
        workflow_id (str): The UUID of the workflow to run.
        inputs (dict): Initial input state.
    """

    workflow_id: Annotated[str, Field(description="The UUID of the workflow definition to instantiate.")]
    inputs: Annotated[
        dict[str, Any],
        Field(description="Key-value pairs representing the initial input state (e.g., source text, user intent)."),
    ] = {}


# --- Workflows ---


@router.post(
    "/workflows", summary="Create Workflow", response_description="A confirmation object with the new Workflow ID."
)
async def create_workflow(request: ExecutionWorkflowCreateRequest, engine: EngineDep):
    """Creates a new workflow definition in the database.

    Args:
        request (ExecutionWorkflowCreateRequest): The workflow payload containing name and steps.
        engine (WorkflowEngine): The workflow engine dependency.

    Returns:
        dict: The status and generated workflow_id.

    """
    workflow_id = await engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}


# --- Executions ---


@router.post(
    "/executions",
    summary="Start Execution",
    response_description="The ID of the newly started execution background job.",
)
async def execute_workflow(
    request: Request,
    json_payload: Annotated[str, Form(alias="json_payload")],
    background_tasks: BackgroundTasks,
    engine: EngineDep,
    current_user: CurrentUserDep,
):
    """Initiates a new workflow execution asynchronously.

    Supports Multipart/Form-Data for optional file uploads alongside JSON inputs.

    Args:
        request (Request): The raw FastAPI request (for parsing file keys).
        json_payload (str): The raw JSON string containing execution config.
        background_tasks (BackgroundTasks): Logic for handling async operations.
        engine (WorkflowEngine): The workflow engine dependency.
        current_user (CurrentUserDep): The authenticated user initiating the run.

    Returns:
        dict: The status and execution_id.
    """
    # Quota Enforcement (Phase 5)
    logger.info("[Router] Trace: 1. Request Received. Checking Quota...")
    from backend.services.usage_service import UsageService

    usage_service = UsageService(engine.repository)
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization.")
    if not await usage_service.check_quota(current_user.organization_id):
        raise HTTPException(status_code=402, detail="Organization Quota Exceeded. Please upgrade your tier.")

    try:
        logger.info("[Router] Trace: 2. Quota OK. Processing Payload...")

        # Parse & Validate Payload Manually (Robustness)
        try:
            request_data = ExecutionRequest.model_validate_json(json_payload)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON Payload: {str(e)}") from e

        # Map Pydantic Schema to Internal Logic
        workflow_id = request_data.project_id
        inputs = request_data.settings

        # GUARD 1: Fail Fast - Check if Workflow Exists (Sync)
        wf_exists = await engine.repository.get_workflow_by_id(workflow_id)
        if not wf_exists:
            raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")

        # Parse Files (Dynamic Keys via Request.form)
        form = await request.form()
        files_map = {}
        for key, value in form.items():
            # Check for StarletteUploadFile (robustness)
            if isinstance(value, (UploadFile, StarletteUploadFile)) and value.filename:
                content = await value.read()
                files_map[key] = (value.filename, content)

        # GUARD 2: Check Required Files/Inputs (Simple Heuristic for Phase 2)
        # If workflow has 'audit' in name, expect standard evidence keys (file OR text)
        if "audit" in workflow_id.lower() or "audit" in wf_exists.get("name", "").lower():
            required_keys = ["history_text", "product_text", "reflection_text"]

            # SCAVENGE: Check for missing keys in the raw form data
            # (Dio/Flutter on Web might send files as simple form fields if content-type is text)
            for key in required_keys:
                if key not in files_map and key not in inputs and key in form:
                    val = form[key]
                    if isinstance(val, str):
                        inputs[key] = val
                    elif isinstance(val, (UploadFile, StarletteUploadFile)):
                        content = await val.read()
                        # Use filename if available, else key name + .txt
                        fname = val.filename or f"{key}.txt"
                        files_map[key] = (fname, content)

            missing = [k for k in required_keys if k not in files_map and k not in inputs]
            if missing:
                raise HTTPException(
                    status_code=400, detail=f"Missing required evidence files for Audit: {', '.join(missing)}"
                )

        logger.info(f"[Router] Trace: 3. Payload Validated. Files: {len(files_map)}. Writing to DB/Storage...")

        # Inject User Identity into Execution Record
        execution_id = await engine.create_execution(
            workflow_id=workflow_id,
            inputs=inputs,
            files=files_map,
            organization_id=current_user.organization_id,
            user_id=current_user.uid,
        )

        logger.info(f"[Router] Trace: 4. DB Write Success (ID: {execution_id}). Fetching cleaned inputs...")

        # Fetch actual text inputs from DB for the runner
        rec = await engine.repository.get_execution(execution_id)
        if not rec:
            raise HTTPException(status_code=500, detail="Execution created but not found.")
        cleaned_inputs = rec.get("inputs", {})

        # DEBUG: Verify inputs made it
        input_summary = {k: len(str(v)) for k, v in cleaned_inputs.items()}
        logger.info(
            f"[Router] Triggering execution {execution_id} for User {current_user.uid} "
            f"(Org: {current_user.organization_id}). Input sizes: {input_summary}"
        )

        background_tasks.add_task(
            engine.run_execution, execution_id, cleaned_inputs, arq_pool=getattr(request.app.state, "arq_pool", None)
        )

        logger.info("[Router] Trace: 5. Background Task Queued. Returning Response.")

        return {"status": "started", "execution_id": execution_id}
    except Exception as e:
        logger.exception("CRITICAL FAILURE IN EXECUTION SUBMISSION")
        # Propagate specific HTTP Exceptions
        if isinstance(e, HTTPException):
            raise e
        # Convert 500s to 400s with visible messages for debugging
        raise HTTPException(status_code=400, detail=f"Submission Error: {str(e)}") from e


@router.get(
    "/executions/recent",
    summary="List Recent Executions",
    response_description="A list of recent execution records, sorted by time (descending).",
)
async def get_recent_executions(
    engine: EngineDep,
    current_user: CurrentUserDep,
    limit: int = APIQuery(5, description="Maximum number of executions to return."),
    status: str | None = APIQuery(None, description="Filter by execution status (e.g., 'completed', 'failed')."),
):
    """Retrieves a list of the most recent workflow executions (Scoped by Org)."""
    # 1. Tenant Scope (Root sees all, others confined to Org)
    scope_org_id = current_user.organization_id if current_user.role != UserRole.ROOT else None

    # 2. User Scope (Members see only own, Managers/Admins see all in Org)
    scope_user_id = None
    if current_user.role == UserRole.MEMBER:
        scope_user_id = current_user.uid

    all_execs = await engine.repository.get_all_executions(organization_id=scope_org_id, user_id=scope_user_id)
    if not all_execs:
        return []

    if status:
        all_execs = [ex for ex in all_execs if ex.get("status", "").lower() == status.lower()]

    sorted_execs = sorted(all_execs, key=lambda x: x.get("start_time", ""), reverse=True)
    return sorted_execs[:limit]


@router.get(
    "/executions/latest",
    summary="Get Latest Execution",
    response_description="The single most recent execution record.",
)
async def get_latest_execution(engine: EngineDep):
    """Retrieves the absolutely most recent execution record."""
    all_execs = await engine.repository.get_all_executions()
    if not all_execs:
        raise HTTPException(status_code=404, detail="No executions found")

    return sorted(all_execs, key=lambda x: x.get("start_time", ""), reverse=True)[0]


@router.get(
    "/executions/{execution_id}",
    summary="Get Execution Status",
    response_description="The detailed status, result, and state of a specific execution.",
)
async def get_execution_status(
    engine: EngineDep, execution_id: str = Path(..., description="The UUID of the execution to retrieve.")
):
    """Retrieves the full status and result data for a specific execution ID.

    Performs on-the-fly hydration of legacy result structures if necessary.
    """
    status = await engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")

    # If the workflow is complete and we have a final result state, flatten it for the UI
    if status.get("status") == "completed" and "result" in status:
        res = status["result"]

        if hasattr(res, "to_flat_dict"):
            status["result"] = res.to_flat_dict()

        elif isinstance(res, dict):
            # CHECK IF ALREADY FLAT (V2 Structure)
            if "Report" in res or "Raw_Steps" in res:
                pass  # Already processed, return as is.
            else:
                # MIGRATION LOGIC:
                # Even if it's already a dict, it might be the OLD structure (nested steps).
                # We want to force it through the new 'to_flat_dict' logic to get the 2-layer structure.
                try:
                    # INJECT MISSING REQUIRED FIELDS for hydration
                    hydration_data = res.copy()
                    if "execution_id" not in hydration_data:
                        hydration_data["execution_id"] = status.get("execution_id", "unknown")
                    if "inputs" not in hydration_data:
                        hydration_data["inputs"] = status.get("inputs", {})

                    # Attempt to hydrate the dict back into a State Object
                    hydrated_state = WorkflowState(**hydration_data)
                    status["result"] = hydrated_state.model_dump()

                except Exception as e:
                    logger.warning(f"Failed to migrate legacy execution result {execution_id}: {e}")
                    # Fallback: leave it as is, legacy UI might handle parts of it
                    pass

    return status


@router.post(
    "/executions/{execution_id}/retry",
    summary="Retry Execution",
    response_description="Confirmation that the execution is resuming.",
)
async def retry_execution(
    background_tasks: BackgroundTasks,
    engine: EngineDep,
    execution_id: str = Path(..., description="The UUID of the execution to retry."),
):
    """Resumes a failed, rejected, or interrupted execution from its last successful state."""
    status = await engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")

    current_status = status.get("status")
    if current_status not in ["failed", "rejected", "interrupted"]:
        raise HTTPException(status_code=400, detail=f"Cannot retry execution in status '{current_status}'.")

    background_tasks.add_task(engine.resume_execution, execution_id)
    return {"status": "resuming", "execution_id": execution_id}
