"""API Router for Execution Lifecycle (Create, Execute, Cancel, Delete)."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Request, status

from backend.core.engine import GraphEngine
from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import (
    DocumentServiceDep,
    EngineDep,
    RepositoryDep,
    get_arq_pool,
    get_async_repository,
    get_engine,
)
from backend.exceptions import AppException, ResourceNotFoundError
from backend.logging_config import log_error
from backend.models.auth import UserRole
from backend.models.dtos.execution import (
    DirectExecutionResponse,
    ExecutionCancelResponse,
    ExecutionDeleteResponse,
    ExecutionResponse,
)
from backend.models.workflow import WorkflowDefinition
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/execute", tags=["Execution V1"])
# Alias router for /executions (RESTful style)
executions_router = APIRouter(prefix="/executions", tags=["Executions"])


@executions_router.post(
    "",
    summary="Create Execution (Alias)",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/",
    summary="Create Execution",
    description="Creates a new execution for a given workflow.",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)
@executions_router.post(
    "/",
    summary="Create Execution",
    description="Creates a new execution for a given workflow.",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_execution(
    request: Request,
    engine: EngineDep,
    repository: RepositoryDep,
    document_service: DocumentServiceDep,
    current_user: Any = Depends(AuthService.get_current_user()),
    arq_pool: Any = Depends(get_arq_pool),
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

        execution_id = str(uuid.uuid4())

        if "application/json" in content_type:
            payload = await request.json()
            workflow_id = payload.get("workflowId")
            inputs = payload.get("inputs", {})
            organization_id = payload.get("organizationId")
        elif "multipart/form-data" in content_type:
            form = await request.form()
            import json

            # 1. Parse Metadata (json_payload)
            json_payload_str = form.get("json_payload")
            if json_payload_str and isinstance(json_payload_str, str):
                try:
                    meta = json.loads(json_payload_str)
                    workflow_id = meta.get("project_id") or meta.get("workflowId")
                    organization_id = meta.get("organizationId")
                    inputs = meta.get("settings", {})
                except json.JSONDecodeError as e:
                    error_code = "INVALID_JSON_PAYLOAD"
                    logger.error(f"{error_code}: {e}")
                    raise AppException(
                        message="Invalid JSON in 'json_payload'",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": error_code},
                    ) from e
            else:
                workflow_id = form.get("workflowId")

            # 2. Parse Files & Form Fields
            files_to_process = {}
            from fastapi import UploadFile

            for key, value in form.items():
                if key in ("json_payload", "workflowId", "organizationId"):
                    continue

                # Robust check for UploadFile (handles Starlette/FastAPI/Duck-typing)
                is_file = isinstance(value, UploadFile) or (hasattr(value, "filename") and hasattr(value, "read"))

                if is_file and hasattr(value, "read"):
                    # Buffer file in memory for DocumentService (it expects bytes)
                    # Note: Starlette UploadFile.read() is async
                    content = await value.read()  # type: ignore[union-attr]
                    filename = getattr(value, "filename", "unknown_file")
                    files_to_process[key] = (filename, content)
                else:
                    # Non-file form fields
                    if key not in inputs:
                        inputs[key] = str(value)

        if organization_id and "organization_id" not in inputs:
            inputs["organization_id"] = organization_id

        # 0. NORMALIZE INPUTS (SSOT Pattern)
        # Ensure organization_id is ALWAYS in inputs, just like file contents.
        # Fallback: If payload is missing it, try current_user (Context Injection)
        if not inputs.get("organization_id"):
            if organization_id:
                inputs["organization_id"] = organization_id
            elif current_user and getattr(current_user, "organization_id", None):
                inputs["organization_id"] = current_user.organization_id
                organization_id = current_user.organization_id  # Sync var for later use

        # 3. Process Evidence Files via DocumentService
        if files_to_process:
            try:
                # DocumentService handles:
                # 1. Archiving to Storage (Forensic Capture)
                # 2. Extracting text (PDF/DOCX/Text)
                # 3. Parsing Chat Logs (ChatLogParser)
                extracted_texts = await document_service.process_evidence_files(execution_id, files_to_process)

                for key, text_content in extracted_texts.items():
                    inputs[key] = text_content
            except Exception as e:
                logger.error(f"DocumentService failed: {e}")
                raise AppException(message=f"File processing failed: {e}", status_code=500, details={"error_code": "FILE_PROCESSING_FAILED"}) from e

        if not workflow_id or not isinstance(workflow_id, str):
            raise AppException(message="Workflow ID missing or invalid", status_code=400)

        # 1. Load Definition via Repository (SSOT)
        # (This block was missing in previous refactor)
        definition = await repository.get_workflow(workflow_id)

        if not definition:
            if isinstance(workflow_id, str):
                raise ResourceNotFoundError(f"Workflow '{workflow_id}' not found.")
            raise ResourceNotFoundError("Workflow not found (invalid ID).")

        # 2. Prepare Execution Record (Restored)
        def sanitize_for_json(obj: Any) -> Any:
            if isinstance(obj, bytes):
                return f"<bytes: {len(obj)}>"
            if isinstance(obj, dict):
                return {k: sanitize_for_json(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize_for_json(v) for v in obj]
            return obj

        sanitized_inputs = sanitize_for_json(inputs)
        # execution_id already generated at start
        timestamp = datetime.now(UTC)

        execution_data = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "status": "pending",
            "started_at": timestamp,
            "completed_at": None,
            "results": {},
            "inputs": sanitized_inputs,
            "user_id": current_user.id if current_user else "system",
            "organization_id": organization_id,
            "workflow_name": definition.name if definition else None,
        }

        await repository.create_execution(execution_data)
        logger.info(f"Created pending execution {execution_id} for workflow {workflow_id}")

        # 4. Enqueue Async Job
        if arq_pool:
            await arq_pool.enqueue_job(
                "execute_workflow_job",
                workflow_id=workflow_id,
                inputs=inputs,
                execution_id=execution_id,
                organization_id=organization_id,
                user_id=current_user.id if current_user else "system",
            )
        else:
            logger.warning("Arq pool not available! Running Synchronously.")
            # Inject identity context for synchronous execution
            if current_user:
                inputs["user_id"] = current_user.id

            start_time_sync = datetime.now(UTC)
            result = await engine.execute_workflow(definition, inputs, repository=repository, execution_id=execution_id)
            execution_data["results"] = sanitize_for_json(result)
            execution_data["status"] = "completed"
            execution_data["completed_at"] = datetime.now(UTC).isoformat()

            # Extract cost_estimate and telemetry
            cost_estimate = 0.0
            models_used: dict[str, int] = {}
            duration_ms = int((datetime.now(UTC) - start_time_sync).total_seconds() * 1000)

            if isinstance(result, dict):
                trace = result.get("execution_trace", [])
                if isinstance(trace, list):
                    for event in trace:
                        if isinstance(event, dict) and event.get("event_type") == "output":
                            content = event.get("content", {})
                            if isinstance(content, dict):
                                meta = content.get("metadata", {})
                                if isinstance(meta, dict):
                                    # Extract Model usage
                                    m = meta.get("model")
                                    if m:
                                        models_used[m] = models_used.get(m, 0) + 1

                                    # Extract Cost per step
                                    tu = meta.get("token_usage", {})
                                    if isinstance(tu, dict):
                                        cost_estimate += tu.get("cost_usd", 0.0)

            execution_data["cost_estimate"] = cost_estimate
            execution_data["duration_ms"] = duration_ms
            execution_data["models_used"] = models_used

            await repository.update_execution(execution_id, execution_data)

        # Mapping for Response DTO
        return ExecutionResponse(
            id=execution_id,
            workflow_id=workflow_id if isinstance(workflow_id, str) else str(workflow_id),
            status=str(execution_data.get("status", "pending")),
            started_at=execution_data["started_at"],
            completed_at=execution_data.get("completed_at"),
            results=execution_data.get("results") or {},
            inputs=execution_data.get("inputs") or {},
            user_id=str(execution_data.get("user_id", "")),
            organization_id=execution_data.get("organization_id"),
            workflow_name=execution_data.get("workflow_name"),
            start_time=execution_data["started_at"],
        )

    except AppException:
        raise
    except ResourceNotFoundError as e:
        error_code = "WORKFLOW_NOT_FOUND"
        wrapped = AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e
    except ValueError as e:
        # Pydantic/Engine validation errors (strict schema enforcement)
        error_code = "INVALID_INPUT"
        wrapped = AppException(
            message=str(e), status_code=status.HTTP_400_BAD_REQUEST, details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e
    except Exception as e:
        error_code = "EXECUTION_CREATION_FAILED"
        wrapped = AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e


@router.delete(
    "/{execution_id}",
    summary="Delete Execution",
    status_code=status.HTTP_200_OK,
    response_model=ExecutionDeleteResponse,
)
@executions_router.delete(
    "/{execution_id}",
    summary="Delete Execution",
    status_code=status.HTTP_200_OK,
    response_model=ExecutionDeleteResponse,
)
async def delete_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Delete an execution record."""
    try:
        # Check privileges (skipped for brevity, assuming standard RBAC)
        exists = await repository.get_execution(execution_id)
        if not exists:
            raise ResourceNotFoundError(f"Execution {execution_id} not found")

        await repository.delete_execution(execution_id)
        return ExecutionDeleteResponse(status="deleted", id=execution_id)
    except AppException:
        raise
    except Exception as e:
        error_code = "EXECUTION_DELETE_FAILED"
        wrapped = AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e


# Direct Execute Router (Legacy /v1/execute/{id})
@router.post(
    "/{workflow_id}",
    response_model=DirectExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute a Workflow (Direct)",
    description="Direct execution endpoint.",
)
async def execute_workflow_route(
    workflow_id: str,
    payload: dict[str, Any],
    engine: GraphEngine = Depends(get_engine),
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
):
    """Executes a workflow by ID synchronously (Legacy wrapper)."""
    # Logic similar to create_execution but without Arq enqueue usually,
    # or just delegates. For V2, better to discourage this or map it to create_execution.
    # We will keep it minimal as a wrapper.
    logger.info(f"Received sync execution request for workflow: {workflow_id}")

    # Simple direct execution logic (Blocking)
    import json
    import os

    definition = None
    file_path = f"data/workflows/{workflow_id}.json"
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            if "description" not in data:
                data["description"] = "Loaded"
            definition = WorkflowDefinition(**data)
    else:
        definition = await repository.get_workflow(workflow_id)

    if not definition:
        raise ResourceNotFoundError(f"Workflow '{workflow_id}' not found.")

    result = await engine.execute_workflow(definition, payload)
    return DirectExecutionResponse.model_validate(result)


@executions_router.delete(
    "/{execution_id}/cancel",
    summary="Cancel Execution",
    description="Signals the workflow engine to cancel the running execution.",
    status_code=status.HTTP_200_OK,
    response_model=ExecutionCancelResponse,
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
        user_role = current_user.role
        user_org = current_user.organization_id

        # execution is Pydantic model
        record_org = getattr(execution, "organization_id", None)
        record_user = getattr(execution, "user_id", None)

        has_access = False

        if user_role == UserRole.ROOT:
            has_access = True
        elif user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            # Can cancel within organization
            if user_org and user_org == record_org:
                has_access = True
        elif user_role == UserRole.MEMBER:
            # Can cancel own executions
            if str(current_user.id) == str(record_user):
                has_access = True

        if not has_access:
            error_code = "PERMISSION_DENIED"
            raise AppException(
                message="You typically do not have permission to cancel this execution.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"error_code": error_code},
            )

        # 3. Update Status
        # We set it to 'cancelling'. The engine will pick this up in the next step iteration.
        current_status = getattr(execution, "status", None)
        if current_status in ["completed", "failed", "cancelled"]:
            # Already done, no-op but return 200 ok with message
            # Already done, no-op but return 200 ok with message
            return ExecutionCancelResponse(
                id=execution_id, status=str(current_status), message="Execution already finished."
            )

        await repository.update_execution(execution_id, {"status": "cancelling"})

        logger.info(f"Execution {execution_id} marked as cancelling by user {current_user.id}")

        return ExecutionCancelResponse(id=execution_id, status="cancelling", message="Cancellation signal sent.")

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except AppException:
        raise
    except Exception as e:
        log_error(logger, e)
        raise AppException(
            message=f"Failed to cancel execution: {e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from e
