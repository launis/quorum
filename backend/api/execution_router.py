"""Execution Router (V2).

Exposes the GraphEngine for dynamic workflow execution and schema retrieval.
Adheres to Server-Driven UI patterns and One Truth Error Handling.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from backend.api.bff_transformer import ReportTransformer
from backend.settings import get_settings

# Force-register tasks by importing them
from backend.core.engine import GraphEngine
from backend.core.registry import TaskRegistry
from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_arq_pool, get_async_repository, get_engine, StorageDep, get_storage_service_dep
from backend.services.storage import LocalFileStorage, AbstractStorage
from backend.exceptions import AppException, ResourceNotFoundError, WorkflowExecutionError, ErrorCodes
from backend.logging_config import log_error
from backend.models.auth import TokenData, UserRole
from backend.models.view import ReportView
from backend.models.workflow import WorkflowDefinition
from backend.schemas.error import APIError
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/execute", tags=["Execution V1"])
workflow_router = APIRouter(prefix="/v1/workflow", tags=["Workflow V1"])
executions_router = APIRouter(prefix="/executions", tags=["Executions"])


# --- Models ---
# Basic usage doesn't need input model if we accept dict, but for docs:
class ExecutionRequest(BaseModel):
    inputs: dict[str, Any]


# --- Endpoints ---


@router.post(
    "/{workflow_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Execute a Workflow",
    description="Executes a defined workflow using the GraphEngine.",
    responses={
        404: {"model": APIError, "description": "Workflow resource not found"},
        400: {"model": APIError, "description": "Validation error"},
        422: {"model": APIError, "description": "Input schema validation failed"},
        500: {"model": APIError, "description": "Internal execution error"},
    },
)
async def execute_workflow_route(
    workflow_id: str,
    payload: dict[str, Any],  # Dynamic Input
    engine: GraphEngine = Depends(get_engine),
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
):
    """Executes a workflow by ID with provided inputs.

    1. Fetches WorkflowDefinition from DB/Repository.
    2. Validates and executes via GraphEngine.
    """
    logger.info(f"Received execution request for workflow: {workflow_id}")

    try:
        # 1. Load Definition
        # In a real scenario, this comes from DB.
        # For Phase 4.1 testing, if not in DB, we rely on Mock or File loaded?
        # The prompt says "Load the workflow definition".
        # Repository should handle logic.

        # MOCK LOADING FOR NOW if not using live DB or if DB empty
        # We can implement a "get_workflow" in the repository dependency?
        # Or, to ensure this works immediately with the JSON file we created:
        import json
        import os

        definition = None

        # Try Loading from file system if strictly Dev Mode?
        # Ideally Repository abstraction handles this.
        # Let's assume Repository has `get_workflow(id: str) -> WorkflowDefinition`
        # But `AsyncRepository` interface needs verification.

        # Fallback/Direct Load for testing as per common pattern in previous steps
        # If workflow_id == "comprehensive_audit_v1":
        file_path = f"data/workflows/{workflow_id}.json"

        if os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                # Add missing description if schema requires it but file missing it?
                if "description" not in data:
                    data["description"] = "Loaded from file"
                definition = WorkflowDefinition(**data)
        else:
            # Try repository
            definition = await repository.get_workflow(workflow_id)

        if not definition:
            raise ResourceNotFoundError(f"Workflow '{workflow_id}' not found.")

        # 2. Execute
        result = await engine.execute_workflow(definition, payload)

        return result

    except ResourceNotFoundError as e:
        if "error_code" not in e.details:
            e.details["error_code"] = "WORKFLOW_NOT_FOUND"
        log_error(logger, e)
        raise e

    except WorkflowExecutionError as e:
        # Catch structured engine errors
        if "error_code" not in e.details:
            e.details["error_code"] = "WORKFLOW_EXECUTION_FAILED"
        log_error(logger, e, message=f"Execution failed at step '{e.step_id}'")
        raise e

    except Exception as e:
        log_error(logger, e, message="Unexpected execution failure")
        raise e


@workflow_router.get(
    "/{workflow_id}/schema",
    summary="Get Workflow Input Schema",
    description="Returns the JSON Schema for the inputs required by the workflow's first step.",
    response_model=dict[str, Any],
)
async def get_workflow_schema(workflow_id: str, repository: AbstractWorkflowRepository = Depends(get_async_repository)):
    """Generates the Input Schema for Server-Driven UI.

    Logic:
    1. Loads WorkflowDefinition.
    2. Identifies the first step.
    3. Lookups the Task in TaskRegistry.
    4. Returns Task.input_schema.model_json_schema().
    """
    try:
        # 1. Load
        import json
        import os

        definition = None

        # Similar loading logic (Should be unified)
        file_path = f"data/workflows/{workflow_id}.json"

        if os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                definition = WorkflowDefinition(**data)
        else:
            definition = await repository.get_workflow(workflow_id)  # Hypothetical Interface

        if not definition:
            raise ResourceNotFoundError(f"Workflow '{workflow_id}' not found.")

        if not definition.steps:
            raise ResourceNotFoundError("Workflow has no steps.")

        # 2. First Step
        first_step = definition.steps[0]
        task_key = first_step.task_key

        # 3. Registry Lookup
        task_def = TaskRegistry.get(task_key)
        if not task_def:
            raise ResourceNotFoundError(f"Task '{task_key}' not registered.")

        # 4. Schema
        # Note: If inputs are mapped from existing state, this might be misleading?
        # But for the *Start* of the workflow, we usually want the schema of the first task
        # assuming it takes Raw Input.

        # Ideally, we should check which inputs in the First Step are NOT mapped from `$` (state).
        # But usually Step 1 Input = User Input.

        return task_def.input_schema.model_json_schema()

    except ResourceNotFoundError as e:
        if "error_code" not in e.details:
            e.details["error_code"] = "RESOURCE_NOT_FOUND"
        log_error(logger, e)
        raise e
    except Exception as e:
        error_code = "SCHEMA_GENERATION_FAILED"
        wrapped_error = AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        )
        log_error(logger, wrapped_error, message="Schema generation failed")
        raise wrapped_error from e


@executions_router.get("/recent", summary="Get Recent Executions", response_model=list[dict[str, Any]])
async def get_recent_executions(
    limit: int = 10,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get a list of recent executions."""
    try:
        # Resolve user context if needed for RLS
        # current_user is a TokenData object

        # If user is ROOT/ADMIN, maybe see all?
        # For now, simplistic approach: get all (repository usually filters by user if we implemented that)
        # The repository.get_all_executions method signature:
        # get_all_executions(organization_id=None, user_id=None)

        # If we use current_user info:
        # executions = await repository.get_all_executions(user_id=current_user.uid)
        # But for 'Recent' dashboard, usually we see own or org's.

        # Let's pass user_id to be safe and efficient if user is provided.
        # If current_user dependency is enforced, we have uid.

        user_id = current_user.uid if current_user else None

        executions = await repository.get_all_executions(user_id=user_id)

        # Sort in memory (Repository get_all might not sort)
        # Assuming 'created_at' or 'timestamp' field
        # We need to robustly handle missing timestamp
        def get_time(e):
            return e.get("started_at") or e.get("timestamp") or ""

        executions.sort(key=get_time, reverse=True)

        # MAP ID -> EXECUTION_ID & STARTED_AT -> START_TIME (Frontend Contract)
        results = []
        for e in executions[:limit]:
            # Create a copy to avoid mutating cache/db reference if applicable
            item = e.copy()
            if "execution_id" not in item and "id" in item:
                item["execution_id"] = item["id"]

            # Map started_at -> start_time
            if "start_time" not in item:
                item["start_time"] = (
                    item.get("started_at") or item.get("timestamp") or datetime.now(timezone.utc)
                )

            # Ensure 'result' exists for strict contract (Execution.completed requires it)
            if "results" in item and "result" not in item:
                item["result"] = item["results"]  # Legacy mapping
            if "result" not in item:
                item["result"] = {}

            results.append(item)

        return results

    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        wrapped_error = AppException(
            message="Failed to fetch recent executions",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        )
        log_error(logger, wrapped_error)
        raise wrapped_error from e


@executions_router.get("/{execution_id}", summary="Get Execution Details", response_model=dict[str, Any])
async def get_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get execution details by ID.
    Ensures frontend contract compliance (execution_id, start_time, result).
    """
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Contract Mapping
        item = execution.copy()
        if "execution_id" not in item and "id" in item:
            item["execution_id"] = item["id"]

        if "start_time" not in item:
            item["start_time"] = (
                item.get("started_at") or item.get("timestamp") or datetime.now(timezone.utc)
            )

        if "results" in item and "result" not in item:
            item["result"] = item["results"]
        if "result" not in item:
            item["result"] = {}

        return item

    except ResourceNotFoundError as e:
        if "error_code" not in e.details:
            e.details["error_code"] = "EXECUTION_NOT_FOUND"
        log_error(logger, e)
        # Exception handler handles conversion to 404 based on exception type if needed,
        # or we explicitly raise AppException.
        # ResourceNotFoundError usually maps to 404 in main handler if it inherits from it.
        # But here logic explicitly converts to AppException(404).
        # To maintain exact behavior:
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        wrapped = AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e


@executions_router.get(
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
    """Get complete raw execution data for debugging/reporting.

    Returns:
        - All agent step outputs (step_guard, step_analyst, etc.)
        - aux_data with hook outputs
        - Timing information
        - Full workflow state
    """
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Return raw data without transformation
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

        # Calculate duration if completed
        if raw_data["started_at"] and raw_data["completed_at"]:
            try:
                from datetime import datetime

                start = datetime.fromisoformat(raw_data["started_at"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(raw_data["completed_at"].replace("Z", "+00:00"))
                raw_data["duration_seconds"] = (end - start).total_seconds()
            except Exception:
                pass

        # Extract key agent outputs from results
        results = raw_data["results"]
        raw_data["agent_outputs"] = {
            key: results.get(key)
            for key in [
                "step_guard",
                "step_analyst",
                "step_profiler",
                "step_logician",
                "step_falsifier",
                "step_causal",
                "step_detector",
                "step_overseer",
                "step_archivist",
                "step_judge",
                "step_coach",
                "step_xai",
            ]
            if results.get(key)
        }

        # Extract aux_data (hook outputs)
        raw_data["hook_outputs"] = results.get("aux_data", {})

        # Extract XAI report if available
        raw_data["xai_report"] = results.get("xai_report_formatted", "")

        return raw_data

    except ResourceNotFoundError as e:
        if "error_code" not in e.details:
            e.details["error_code"] = "EXECUTION_NOT_FOUND"
        log_error(logger, e)
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


print("Loading Execution Router module...")

from datetime import UTC

from fastapi import Request
from starlette.datastructures import UploadFile


@executions_router.post(
    "",
    summary="Create Execution (Alias)",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@executions_router.post(
    "/",
    summary="Create Execution",
    description="Creates a new execution for a given workflow.",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
async def create_execution(
    request: Request,
    engine: GraphEngine = Depends(get_engine),
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
    arq_pool: Any = Depends(get_arq_pool),  # Any for now to avoid import hell if imports missing
):
    """Creates and starts a workflow execution.
    Handles both JSON and Multipart payloads.
    """
    try:
        content_type = request.headers.get("content-type", "")
        payload = {}
        inputs = {}
        workflow_id = None
        organization_id = None

        if "application/json" in content_type:
            payload = await request.json()
            workflow_id = payload.get("workflowId")
            inputs = payload.get("inputs", {})
            organization_id = payload.get("organizationId")
        elif "multipart/form-data" in content_type:
            form = await request.form()

            # 1. Parse Metadata (json_payload)
            import json

            json_payload_str = form.get("json_payload")
            if json_payload_str:
                try:
                    meta = json.loads(json_payload_str)
                    workflow_id = meta.get("project_id") or meta.get("workflowId")
                    organization_id = meta.get("organizationId")
                    # Merge text inputs from metadata
                    inputs = meta.get("settings", {})
                except json.JSONDecodeError as e:
                    error_code = "INVALID_JSON_PAYLOAD"
                    logger.error(f"{error_code}: {e}")
                    raise AppException(
                        message="Invalid JSON in 'json_payload'",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": error_code}
                    ) from e
            else:
                # Fallback: Try direct fields (legacy/test)
                workflow_id = form.get("workflowId")

            # 2. Parse Files & Form Fields
            # NUCLEAR OPTION: Raw File Write to guarantee visibility
            # 2. Parse Files & Form Fields

            # DEBUG: Massive Logging for Diagnostics (Jan 2026 Mandate)
            # logger.info(f"[DEBUG] Parsing Form. Items count: {len(form)}")

            for key, value in form.items():
                # DEBUG: Individual Item
                # logger.info(f"[DEBUG] Processing form key: '{key}' | Type: {type(value)}")

                if key == "json_payload":
                    continue
                if key == "workflowId":
                    continue

                # Handle Files
                if isinstance(value, UploadFile):
                    # OPERATIONAL LOG: File Reception
                    logger.info(f"[FILE_UPLOAD] Key='{key}' | Filename='{value.filename}' | Content-Type='{value.content_type}'")

                    # Basic Text Extraction
                    content = await value.read()
                    file_size = len(content)

                    if file_size == 0:
                        logger.warning(f"[FILE_UPLOAD] WARNING: File '{value.filename}' has 0 bytes!")

                    text_content = ""

                    if value.filename.lower().endswith(".pdf"):
                        try:
                            from backend.services.document_service import DocumentService
                            text_content = DocumentService._extract_text_from_pdf(content)
                            logger.info(f"[FILE_UPLOAD] PDF Processed: '{value.filename}' | Extracted Chars: {len(text_content)}")
                        except Exception as e:
                            logger.error(f"[FILE_UPLOAD] PDF Extraction Failed for '{value.filename}': {e}")
                            text_content = f"<pdf_error: {value.filename}>"

                    elif value.filename.lower().endswith(".docx"):
                        try:
                            from backend.services.document_service import DocumentService
                            text_content = DocumentService._extract_text_from_docx(content)
                            logger.info(f"[FILE_UPLOAD] DOCX Processed: '{value.filename}' | Extracted Chars: {len(text_content)}")
                        except Exception as e:
                            logger.error(f"[FILE_UPLOAD] DOCX Extraction Failed for '{value.filename}': {e}")
                            text_content = f"<docx_error: {value.filename}>"

                    elif value.filename.lower().endswith((".txt", ".md", ".json", ".csv", ".log")):
                        try:
                            text_content = content.decode("utf-8")
                            logger.info(f"[FILE_UPLOAD] Text File Processed: '{value.filename}' | Chars: {len(text_content)}")
                        except Exception as e:
                            logger.error(f"[FILE_UPLOAD] Text Decoding Failed for '{value.filename}': {e}")
                            text_content = f"<binary_file: {value.filename}>"
                    else:
                        text_content = f"<file_upload: {value.filename} (size={len(content)})>"
                        logger.info(f"[FILE_UPLOAD] Unhandled File Type: '{value.filename}' | Size: {len(content)} bytes | Preserved as metadata.")

                    if key in ["history_text"] or "chat" in key or "history" in key:
                         # Parsing is now handled centrally in GraphEngine
                         pass

                    inputs[key] = text_content


            # 3. Placeholder Resolution (REMOVED - V5.0 STRICT KEY ENFORCEMENT)
            # We no longer support fuzzy matching. Frontend must send correct keys.
            # If a file is uploaded with key 'history_text', it automatically correctly populates inputs['history_text'].
            # If inputs contain {{FILE:...}} placeholders but no matching file key is found, it will fail naturally (or pass through raw).


                    # If it's a regular field not in json_payload, add it
                    if key not in inputs:
                         # --- AUTO-PARSE CHAT LOGS ---
                        val_str = str(value)
                        # logger.info(f"[DEBUG] Form field '{key}' = '{val_str}'")
                        if key == "history_text":
                             # Parsing is now handled centrally in GraphEngine
                             pass
                        inputs[key] = val_str
        else:
            error_code = "UNSUPPORTED_CONTENT_TYPE"
            logger.error(f"{error_code}: {content_type}")
            raise AppException(
                message=f"Unsupported Content-Type: {content_type}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": error_code}
            )

        # Custom Logging Format (Jan 2026)
        logger.info(f"[EXECUTION CREATION] workflow: {workflow_id}")

        if not workflow_id:
            error_code = "MISSING_WORKFLOW_ID"
            logger.error(f"{error_code}: workflowId not provided")
            raise AppException(
                message="Missing 'workflowId' in payload.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": error_code}
            )

        # Re-use the logic from execute_workflow_route (which was v2/execute/{id})
        # Ideally we refactor to a service method, but for now calling engine directly.

        # 1. Load Definition (Unified Logic)
        import json
        import os

        definition = None

        if organization_id:
            inputs["organization_id"] = organization_id

        # Check DB first? Or File?
        # For now, consistent file fallback pattern:
        file_path = f"data/workflows/{workflow_id}.json"

        if os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                # Ensure description if missing
                if "description" not in data:
                    data["description"] = "Loaded from file"
                definition = WorkflowDefinition(**data)
        else:
            definition = await repository.get_workflow(workflow_id)

        if not definition:
            raise ResourceNotFoundError(f"Workflow '{workflow_id}' not found.")

        # 2. Execute (ASYNC via Worker)
        # We now enqueue the job to the worker instead of running it synchronously.
        # This returns immediately with 'pending' status.

        # Inject dependency (assuming it's available, otherwise we need to get it)
        # We need to add 'arq_pool' to the function signature first!
        # But REPLACING CONTENT here implies I can't easily change the signature 200 lines above.

        # STOP: I need to change the signature of `create_execution` first to include `get_arq_pool`.
        # I cannot do this validly with just this block replacement.
        # 2. Prepare Execution Record (Pending)
        # SANITIZE: Recursively convert bytes to string placeholders to prevent UnicodeDecodeError
        # This is critical as 'inputs' or 'state' may contain raw file bytes (PDFs, etc).
        def sanitize_for_json(obj: Any) -> Any:
            if isinstance(obj, bytes):
                return f"<bytes: {len(obj)}>"
            if isinstance(obj, dict):
                return {k: sanitize_for_json(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize_for_json(v) for v in obj]
            return obj

        sanitized_inputs = sanitize_for_json(inputs)

        # 3. Format & Persist Initial Response (Pending)
        import uuid
        from datetime import datetime

        execution_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC)

        execution_data = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "status": "pending",  # Initial Status
            "started_at": timestamp,
            "completed_at": None,  # Not done yet
            "results": {},  # Empty results initially
            "inputs": sanitized_inputs,
            "inputs": sanitized_inputs,
            "user_id": current_user.uid if current_user else "system",
            "organization_id": organization_id,
        }

        # Persist Initial State
        await repository.create_execution(execution_data)

        # LOGFIRE INTEGRATION: Link API request to Execution ID
        import logfire
        logfire.info("Created execution", tags={"execution_id": execution_id, "workflow_id": workflow_id})

        logger.info(f"Created pending execution {execution_id} for workflow {workflow_id}")

        # 4. Enqueue Async Job
        # Passes execution_id so worker can update this specific record
        if arq_pool:
            await arq_pool.enqueue_job(
                "execute_workflow_job",
                workflow_id=workflow_id,
                inputs=inputs,
                execution_id=execution_id,
                organization_id=organization_id,
            )
            logger.info(f"Enqueued job for execution {execution_id}")
        else:
            # Fallback if ARQ not configured (should trigger 500 in prod, but safe fallback for dumb tests?)
            logger.warning("Arq pool not available! Running Synchronously (blocking) for fallback.")
            # Fallback Sync Run (User won't see pallukat updates real-time but it will finish)
            result = await engine.execute_workflow(definition, inputs, repository=repository, execution_id=execution_id)

            # Update to completed
            completed_time = datetime.now(UTC)
            execution_data["results"] = sanitize_for_json(result)
            execution_data["status"] = "completed"
            execution_data["completed_at"] = completed_time
            await repository.update_execution(execution_id, execution_data)

        # 5. Return Response
        # Conforms to frontend contract
        response_data = execution_data.copy()
        response_data["start_time"] = timestamp
        # Add execution_id explicitly if missing (though it is in 'id')
        response_data["execution_id"] = execution_id

        return response_data

    except AppException:
        raise
    except ResourceNotFoundError as e:
        error_code = "WORKFLOW_NOT_FOUND"
        wrapped = AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e
    except WorkflowExecutionError as e:
        error_code = "WORKFLOW_EXECUTION_FAILED"
        wrapped = AppException(
            message=f"Execution failed: {e.original_error}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "step_id": e.step_id}
        )
        log_error(logger, wrapped, message=f"Workflow execution failed at step {e.step_id}")
        raise wrapped from e
    except Exception as e:
        error_code = "EXECUTION_CREATION_FAILED"
        wrapped = AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e

@executions_router.get(
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
):
    """BFF Endpoint: Transforms raw execution data into a ReportView.
    """
    try:
        # 1. Fetch Raw Data
        # Assuming repository has get_execution. If not, we might need to use generic get/find.
        # TinyDB usually has get_execution(id).
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # 2. Transform
        transformer = ReportTransformer()
        # execution is usually a Pydantic model or dict.
        # If Pydantic, dump to dict.
        if hasattr(execution, "model_dump"):
            raw_data = execution.model_dump()
        elif hasattr(execution, "dict"):
             raw_data = execution.dict()
        else:
            raw_data = execution # Assume dict

        # 3. Dynamic Scale Resolution (Database Authority)
        # Default to standard 1-4
        scale_limit = None  # STRICT: No default. Must be found in DB or Step.

        try:
            matrix_id = None
            # A. Try Result Metadata (Fastest)
            # Check step_judge or step_judge_cognitive
            results = raw_data.get("results", {})
            # Normalized execution result often has 'step_results' key
            if "step_results" in results: steps = results["step_results"]
            else: steps = results

            judge_step = steps.get("step_judge") or steps.get("step_judge_cognitive")
            if judge_step:
                if "matrix_id" in judge_step:
                    matrix_id = judge_step["matrix_id"]
                elif "metadata" in judge_step and "matrix_id" in judge_step["metadata"]:
                    matrix_id = judge_step["metadata"]["matrix_id"] # Uncommon but possible

            # B. Try Input Metadata (Second authority)
            # If not in results, check inputs (maybe seeded)
            if not matrix_id:
                inputs = raw_data.get("inputs", {})
                matrix_id = inputs.get("matrix_id")

            # C. Try Workflow Definition (Default/Static)
            # If still None, load workflow def? (Expensive).
            # We skip for now unless crucial.

        except Exception:
            pass
        
        # 4. Resolve Scale using Matrix Service (or direct DB lookup if simple)
        # For simplicity in BFF: if matrix_id suggests 'binary', use binary.
        # If '1-10', use 10.
        # If dynamic, query DB.
        
        # TODO: Inject MatrixService dependency if we want true dynamic caching here.
        # For now, default 1-4.
        
        view = transformer.transform(raw_data, scale_limit=4) # Default 4 if not resolved

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


# --- PDF Security Helper ---

def _enforce_pdf_access(user: TokenData, execution: dict[str, Any]) -> None:
    """Enforces strict RBAC for PDF access.

    Rules:
    - ROOT: Allow ALL.
    - MANAGER: Allow IF execution.organization_id == user.organization_id.
    - MEMBER (User): Allow IF execution.user_id == user.uid.
    - ADMIN: DENY ALL (per mandate).
    """
    if user.role == UserRole.ROOT:
        return

    if user.role == UserRole.ADMIN:
        # Per mandate: "ADMIN: DENY ALL"
        # Admin manages users, not executions? Unusual but enforced.
        raise AppException(
            message="Admins are not authorized to view execution PDFs.",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"error_code": "ADMIN_DENIED"}
        )

    if user.role == UserRole.MANAGER:
        # Check Organization Match
        exec_org = execution.get("organization_id")
        user_org = user.organization_id
        if exec_org != user_org:
            raise AppException(
                message="Managers can only access executions within their organization.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"error_code": "ORG_MISMATCH", "exec_org": exec_org, "user_org": user_org}
            )
        return

    # Default / MEMBER / Test User
    # Must own the execution
    exec_user = execution.get("user_id")
    if exec_user != user.uid:
        raise AppException(
            message="You do not have permission to access this execution.",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"error_code": "OWNERSHIP_REQUIRED"}
        )


# --- PDF Endpoints ---

@executions_router.get(
    "/{execution_id}/pdf/download",
    summary="Download Execution PDF",
    description="Securely download the PDF report. Enqueues generation if missing.",
)
async def download_execution_pdf(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: TokenData = Depends(AuthService.get_current_user()),
    arq_pool: Any = Depends(get_arq_pool),
    storage: AbstractStorage = Depends(get_storage_service_dep),
):
    """
    1. Enforce RBAC.
    2. Check File Existence (Storage).
    3. Return File OR Queue Job (202 Accepted).
    """
    try:
        # 1. Fetch & Check Access
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution {execution_id} not found")

        # Convert to dict for helper
        exec_data = execution.model_dump() if hasattr(execution, 'model_dump') else execution
        _enforce_pdf_access(current_user, exec_data)

        # 2. Check File
        # Rel path: executions/{id}/report.pdf
        rel_path = f"executions/{execution_id}/report.pdf"
        
        if storage.exists(rel_path):
            # Optimisation for Local Files
            if isinstance(storage, LocalFileStorage):
                full_path = storage.base_path / rel_path
                return FileResponse(
                    path=full_path, 
                    filename=f"report_{execution_id}.pdf", 
                    media_type="application/pdf",
                    content_disposition_type="attachment"
                )
            else:
                # Cloud Storage: Read bytes and return
                content = storage.read(rel_path)
                from fastapi.responses import Response
                return Response(
                    content=content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="report_{execution_id}.pdf"'}
                )

        # 3. Queue Job if missing
        if arq_pool:
            # Check if job already running? Arq doesn't easily expose this without job_id check
            # We'll just enqueue. Idempotency handled by queue or simple overwrite.
            await arq_pool.enqueue_job("generate_pdf_job", execution_id=execution_id)

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={"status": "accepted", "message": "PDF generation queued."}
            )
        else:
            raise AppException(
                message="Background worker unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details={"error_code": "WORKER_UNAVAILABLE"}
            )

    except AppException:
        raise
    except Exception as e:
        error_code = ErrorCodes.PDF_DOWNLOAD_FAILED
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


@executions_router.get(
    "/{execution_id}/pdf/progress",
    summary="Track PDF Generation Progress",
    description="Server-Sent Events (SSE) for PDF generation progress.",
)
async def get_pdf_progress(
    request: Request,
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: TokenData = Depends(AuthService.get_current_user()),
    arq_pool: Any = Depends(get_arq_pool),
):
    """SSE Endpoint for Progress."""
    try:
        # 1. Auth Check
        execution = await repository.get_execution(execution_id)
        if not execution:
            # SSE usually fails silently or closes connection if 404, but we can raise
            raise ResourceNotFoundError(f"Execution {execution_id} not found")

        exec_data = execution.model_dump() if hasattr(execution, 'model_dump') else execution
        _enforce_pdf_access(current_user, exec_data)

        # 2. Generator
        async def event_generator():
            # In a real scenario, we'd subscribe to Redis PubSub.
            # Simplified: Polling the key set by ProgressService
            import asyncio
            import json

            # We need a Redis client. Arq pool is a client.
            redis = arq_pool
            key = f"progress:{execution_id}:pdf_gen"

            while True:
                if await request.is_disconnected():
                    break

                data_raw = await redis.get(key)
                if data_raw:
                    # Yield data compatible with sse_starlette
                    # It treats dict yield as ServerSentEvent(**dict)
                    # So we must wrap our payload in 'data' key explicitly.
                    yield {"data": data_raw}

                    # Check completion
                    data = json.loads(data_raw)
                    if data.get("progress") >= 1.0 or data.get("progress") < 0:
                        break
                else:
                    # Maybe job hasn't started? Yield init?
                    yield {"data": json.dumps({"progress": 0.0, "message": "Waiting for worker..."})}

                await asyncio.sleep(0.5)

        return EventSourceResponse(event_generator())

    except Exception as e:
        log_error(logger, e)
        raise AppException(str(e), 500)


@executions_router.delete(
    "/{execution_id}/pdf/cancel",
    summary="Cancel PDF Generation",
    description="Cancels the download process and cleans up files.",
)
async def cancel_pdf_generation(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: TokenData = Depends(AuthService.get_current_user()),
):
    """Cancel endpoint (Clean up)."""
    try:
        # 1. Auth Check
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution {execution_id} not found")

        exec_data = execution.model_dump() if hasattr(execution, 'model_dump') else execution
        _enforce_pdf_access(current_user, exec_data)

        # 2. Delete File
        from backend.services.storage import LocalFileStorage, get_storage_client
        storage = get_storage_client()
        rel_path = f"executions/{execution_id}/report.pdf"
        
        if isinstance(storage, LocalFileStorage):
            full_path = storage.base_path / rel_path
            if full_path.exists():
                os.remove(full_path)

        # 3. We can't easily cancel a running Arq job without Job ID,
        # but we can assume client stops listening.
        # Ideally we'd store Job ID in DB. For now, file cleanup + return.

        return {"status": "success", "message": "PDF cancelled and file removed."}

    except Exception as e:
         log_error(logger, e)
         raise AppException(str(e), 500)

# --- NEW ENDPOINTS (Jan 2026) ---

@executions_router.delete(
    "/{execution_id}/cancel",
    summary="Cancel Execution",
    description="Signals the workflow engine to cancel the running execution.",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, Any],
)
async def cancel_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Cancel a running workflow execution."""
    try:
        # 1. Fetch Execution
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")
        
        # 2. RBAC Check
        # Root can cancel anything.
        # Managers of the Org can cancel anything in Org.
        # Members can only cancel their own.
        
        user_role = current_user.role
        user_org = current_user.organization_id
        record_org = execution.get("organization_id")
        record_user = execution.get("user_id")

        has_access = False
        
        if user_role == UserRole.ROOT:
            has_access = True
        elif user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            # Can cancel within organization
            if user_org and user_org == record_org:
                has_access = True
        elif user_role == UserRole.MEMBER:
             # Can cancel own executions
             if str(current_user.uid) == str(record_user):
                 has_access = True
                 
        if not has_access:
            error_code = "PERMISSION_DENIED"
            raise AppException(
                message="You typically do not have permission to cancel this execution.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"error_code": error_code}
            )

        # 3. Update Status
        # We set it to 'cancelling'. The engine will pick this up in the next step iteration.
        current_status = execution.get("status")
        if current_status in ["completed", "failed", "cancelled"]:
            # Already done, no-op but return 200 ok with message
            return {"execution_id": execution_id, "status": current_status, "message": "Execution already finished."}

        await repository.update_execution(execution_id, {"status": "cancelling"})
        
        logger.info(f"Execution {execution_id} marked as cancelling by user {current_user.uid}")

        return {"execution_id": execution_id, "status": "cancelling", "message": "Cancellation signal sent."}

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except AppException:
        raise
    except Exception as e:
        log_error(logger, e)
        raise AppException(
            message=f"Failed to cancel execution: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from e


@executions_router.get(
    "/{execution_id}/events",
    summary="Monitor Execution (SSE)",
    description="Streams real-time execution events via Server-Sent Events (SSE).",
    response_class=EventSourceResponse,
)
async def monitor_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    # Token usually passed in query param for EventSource or use standard header if client supports it
    # We'll use standard dependency for strictness, assume client sends header.
    current_user: Any = Depends(AuthService.get_current_user()),
    settings: Any = Depends(get_settings),
):
    """Subscribe to Redis channel for execution updates (SSE)."""
    import asyncio
    import redis.asyncio as redis 
    import json

    # 1. Existence & Auth Check (Quick verify)
    execution = await repository.get_execution(execution_id)
    if not execution:
         raise HTTPException(status_code=404, detail="Execution not found")

    # Simple RBAC: View permission needed
    # If user can see it in get_execution, they can monitor it.
    if current_user.role != UserRole.ROOT:
        if current_user.organization_id and execution.get("organization_id") != current_user.organization_id:
             raise HTTPException(status_code=403, detail="Access denied")

    async def event_generator():
        # Connect to Redis
        redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"
        try:
            r = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            pubsub = r.pubsub()
            channel = f"progress_updates:{execution_id}"
            await pubsub.subscribe(channel)
            
            # Send initial state
            yield {
                "event": "connected",
                "data": json.dumps({"message": f"Connected to stream for {execution_id}"})
            }

            # Listen loop
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"]
                        # format: {"status": "running", "current_step": "...", "progress": 50, ...}
                        yield {
                            "event": "update",
                            "data": data 
                        }
                        
                        # Stop valid condition?
                        # If data has status 'completed' or 'failed', we might want to close?
                        # Or let client decide.
                        try:
                            payload = json.loads(data)
                            if payload.get("status") in ["completed", "failed", "cancelled"]:
                                # Send one last closure event or just wait for client to disconnect
                                logger.debug(f"Stream {execution_id} finished via channel.")
                                # break # Optional: Uncomment to auto-close stream on server side
                        except:
                            pass

            except asyncio.CancelledError:
                logger.debug(f"Client disconnected from stream {execution_id}")
                raise

        except Exception as e:
            logger.error(f"SSE Error for {execution_id}: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
        finally:
            await r.close()
            # await pubsub.unsubscribe(channel) # implicit in close?

    return EventSourceResponse(event_generator())
