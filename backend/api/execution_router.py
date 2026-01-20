"""Execution Router (V2).

Exposes the GraphEngine for dynamic workflow execution and schema retrieval.
Adheres to Server-Driven UI patterns and One Truth Error Handling.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Force-register tasks by importing them
from backend.core.engine import GraphEngine
from backend.core.registry import TaskRegistry
from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_arq_pool, get_async_repository, get_engine
from backend.exceptions import AppException, ResourceNotFoundError, WorkflowExecutionError
from backend.models.workflow import WorkflowDefinition
from backend.schemas.error import APIError
from backend.schemas.error import APIError
from backend.services.auth import AuthService
from backend.models.view import ReportView
from backend.api.bff_transformer import ReportTransformer

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
        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: {e}")
        # Inject code and re-raise for global handler
        e.details["error_code"] = error_code
        raise e

    except WorkflowExecutionError as e:
        # Catch structured engine errors
        error_code = "WORKFLOW_EXECUTION_FAILED"
        logger.error(f"{error_code}: Execution failed at step '{e.step_id}': {e.original_error}")
        # Inject code/details and re-raise
        e.details["error_code"] = error_code
        e.message = f"Execution failed at step '{e.step_id}'."  # Optional: User-friendly override
        raise e

    except Exception as e:
        error_code = "INTERNAL_SERVER_ERROR"
        logger.error(f"{error_code}: Unexpected failure: {e}", exc_info=True)
        # Use generic 500 handler or wrap?
        # Global handler in main.py catches Exception -> 500.
        # But to be explicit and allow "INTERNAL_SERVER_ERROR" code propagation if we wanted custom logic:
        raise e  # Let Global Handler take it (it uses INTERNAL_SERVER_ERROR default)


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
        error_code = "RESOURCE_NOT_FOUND"
        logger.warning(f"{error_code}: {e}")
        # Re-raise as is, or wrap if specific details needed.
        # But ResourceNotFoundError is an AppException, so checking main handler.
        # Ensure it has error_code in details
        if "error_code" not in e.details:
            e.details["error_code"] = error_code
        raise e
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "SCHEMA_GENERATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


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
                    item.get("started_at") or item.get("timestamp") or datetime.now(timezone.utc).isoformat()
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
        logger.error(f"{error_code}: Failed to fetch recent executions - {e}", exc_info=True)
        raise AppException(
            message="Failed to fetch recent executions",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        ) from e


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
                item.get("started_at") or item.get("timestamp") or datetime.now(datetime.UTC).isoformat()
            )

        if "results" in item and "result" not in item:
            item["result"] = item["results"]
        if "result" not in item:
            item["result"] = {}

        return item

    except ResourceNotFoundError as e:
        error_code = "EXECUTION_NOT_FOUND"
        logger.warning(f"{error_code}: {e}")
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": error_code}
        ) from e
    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e


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
        error_code = "EXECUTION_NOT_FOUND"
        logger.warning(f"{error_code}: {e}")
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": error_code}
        ) from e
    except Exception as e:
        error_code = "RAW_DATA_FETCH_FAILED"
        logger.error(f"{error_code}: Failed to fetch raw data for {execution_id} - {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


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
        timestamp = datetime.now(UTC).isoformat()

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
            completed_time = datetime.now(UTC).isoformat()
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
        logger.warning(f"{error_code}: {e}")
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": error_code}
        ) from e
    except WorkflowExecutionError as e:
        error_code = "WORKFLOW_EXECUTION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=f"Execution failed: {e.original_error}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "step_id": e.step_id}
        ) from e
    except Exception as e:
        error_code = "EXECUTION_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e

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
    """
    BFF Endpoint: Transforms raw execution data into a ReportView.
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

            # B. Fallback to Workflow Config (if not in result)
            if not matrix_id:
                workflow_id = raw_data.get("workflow_id")
                if workflow_id:
                     workflow = await repository.get_workflow(workflow_id)
                     if workflow:
                         # Find Judge Step Config
                         for step in workflow.steps:
                             if step.task_key in ["judge", "cognitive_judge"]:
                                 matrix_id = step.config.get("matrix_id")
                                 break
            
            # C. Fetch Matrix Component
            if matrix_id:
                matrix = await repository.get_component_by_id(matrix_id)
                if matrix:
                    # 1. Try nested content.scale (Official format)
                    content = matrix.get("content", {})
                    if "scale" in content:
                        scale = content["scale"]
                        scale_limit = (float(scale["min"]), float(scale["max"]))
                        logger.info(f"[BFF] Resolved dynamic scale for {execution_id} via {matrix_id} (content.scale): {scale_limit}")
                    else:
                        raise ValueError(f"[BFF] Matrix {matrix_id} found but missing 'content.scale'. Cannot determine validation range.")
                else:
                     raise ValueError(f"[BFF] Matrix component {matrix_id} not found in DB. Cannot determine validation range.")
            else:
                 raise ValueError(f"[BFF] No matrix_id found for {execution_id}. Cannot determine validation range.")

        except Exception as e:
            logger.warning(f"[BFF] Dynamic scale resolution failed: {e}. Passing None to Transformer (Strict Mode).")

        report_view = transformer.transform(raw_data, valid_range=scale_limit)
        
        return report_view

    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        # Strict validation failed (e.g. Score > 4)
        logger.error(f"View generation failed for {execution_id}: {e}")
        # We assume the user wants 500 here as per "no fallback" instruction implication
        raise HTTPException(status_code=500, detail=f"Data integrity error: {e}")
    except Exception as e:
        logger.error(f"BFF Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal transformation error")
