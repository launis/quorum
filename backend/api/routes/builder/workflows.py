"""Builder Workflow Routes.

Handles Creation, Update, Deletion, and Listing of Workflows.
"""

import copy
import logging
import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from backend.dependencies import CurrentUserDep, RepositoryDep
from backend.models.auth import UserRole

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---

class BuilderWorkflowCreateRequest(BaseModel):
    """Payload for creating a new workflow."""
    name: Annotated[str, Field(description="Name of the new workflow.")]
    description: Annotated[str | None, Field(description="Optional description.")] = None
    steps: Annotated[list[str], Field(description="List of step IDs.")] = []
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Initial model mapping.")] = {}
    ui_schema: Annotated[dict[str, Any] | None, Field(description="UI Layout metadata.")] = {}
    is_public: Annotated[bool, Field(description="If True, visible to all tenants (System Only).")] = False
    status: Annotated[str, Field(description="Lifecycle status.")] = "draft"
    version: Annotated[int, Field(description="Version number.")] = 1
    scoring_logic: Annotated[list[dict[str, Any]], Field(description="Scoring configuration.")] = []


class WorkflowUpdateRequest(BaseModel):
    """Payload for updating an existing workflow."""
    name: Annotated[str | None, Field(description="New name.")] = None
    description: Annotated[str | None, Field(description="New description.")] = None
    steps: Annotated[list[str | dict[str, Any]] | None, Field(description="New step sequence (IDs or Full Objects).")] = None
    ui_schema: Annotated[dict[str, Any] | None, Field(description="New UI metadata.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Updated model mapping.")] = None
    is_public: Annotated[bool | None, Field(description="Update visibility.")] = None
    status: Annotated[str | None, Field(description="Update status.")] = None
    version: Annotated[int | None, Field(description="Update version.")] = None
    scoring_logic: Annotated[list[dict[str, Any]] | None, Field(description="Updated scoring configuration.")] = None



class CopyWorkflowRequest(BaseModel):
    """Payload for copying a workflow."""
    new_name: Annotated[str, Field(description="Name for the copy.", json_schema_extra={"x-ui-label": "Workflow Name"})]


# --- Helpers ---

async def _expand_workflow(wf: dict[str, Any], repository: RepositoryDep) -> dict[str, Any]:
    """Hydrates step IDs into full step objects."""
    full_wf = wf.copy()
    step_ids = wf.get("steps", [])
    
    hydrated_steps = []
    for s_id in step_ids:
        # If the DB already has objects (unlikely but possible during migration), keep them.
        if isinstance(s_id, dict):
            hydrated_steps.append(s_id)
            continue
            
        if isinstance(s_id, str):
            step = await repository.get_step_by_id(s_id)
            if step:
                hydrated_steps.append(step)
            else:
                # Step missing? Keep ID as a lightweight placeholder or placeholder object?
                # Frontend expects Map.
                logger.warning(f"Workflow {wf.get('id')} references missing step {s_id}")
                hydrated_steps.append({
                    "id": s_id,
                    "name": "Missing Step",
                    "task_key": "unknown",
                    "is_missing": True
                })

    full_wf["steps"] = hydrated_steps
    return full_wf


# --- Endpoints ---

@router.get("/workflows", summary="List Workflows", response_description="All Workflows.")
async def list_workflows(repository: RepositoryDep, current_user: CurrentUserDep):
    """List all workflows visible to the current user."""
    raw_wfs = await repository.get_all_workflows(organization_id=current_user.organization_id, role=current_user.role)
    return [await _expand_workflow(wf, repository) for wf in raw_wfs]


@router.post("/workflows", summary="Create Workflow", response_description="Created workflow data.")
async def create_workflow(
    request: BuilderWorkflowCreateRequest, repository: RepositoryDep, current_user: CurrentUserDep
):
    """Create a new workflow."""
    # 1. RBAC Check
    if current_user.role not in [UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER]:
        from backend.exceptions import PermissionDeniedError

        error_code = "PERMISSION_DENIED_WORKFLOW_CREATE"
        logger.error(f"{error_code}: User {current_user.uid} (Role {current_user.role}) denied.", exc_info=True)
        raise PermissionDeniedError(message="Permission denied", details={"error_code": error_code})

    # 2. Org Assignment
    target_org = current_user.organization_id or "system"

    # 3. Visibility Check
    is_public_val = False
    if request.is_public:
        if current_user.role != UserRole.ROOT:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_PUBLIC_VISIBILITY"
            logger.error(f"{error_code}: Non-ROOT user {current_user.uid} tried setting public.", exc_info=True)
            raise PermissionDeniedError(
                message="Public visibility restricted to ROOT", details={"error_code": error_code}
            )
        is_public_val = True

    try:
        new_id = str(uuid.uuid4()).split("-")[0]  # Short ID
        workflow_data = {
            "id": f"wf_{new_id}",
            "name": request.name,
            "description": request.description or "",
            "steps": request.steps,
            "default_model_mapping": request.default_model_mapping or {},
            "ui_schema": request.ui_schema or {},
            "created_at": datetime.now(),
            "organization_id": target_org,
            "is_public": is_public_val,

            "status": request.status,
            "version": request.version,
            "scoring_logic": request.scoring_logic,
        }

        await repository.create_workflow(workflow_data)
        
        # Return expanded
        return await _expand_workflow(workflow_data, repository)
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "WORKFLOW_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.get("/workflows/{workflow_id}", summary="Get Workflow", response_description="Workflow details.")
async def get_workflow(workflow_id: str, repository: RepositoryDep):
    """Get details of a specific workflow."""
    logger.info(f"GET Workflow Request. ID: '{workflow_id}'")
    wf = await repository.get_workflow_by_id(workflow_id)
    if not wf:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID '{workflow_id}' not found in Repository. Type: {type(workflow_id)}")
        raise ResourceNotFoundError("Workflow", workflow_id, details={"error_code": error_code})
    logger.info(f"Found workflow: {wf.get('id')} - {wf.get('name')}")
    
    return await _expand_workflow(wf, repository)


@router.put("/workflows/{workflow_id}", summary="Update Workflow", response_description="Updated workflow.")
async def update_workflow(
    workflow_id: str, request: WorkflowUpdateRequest, repository: RepositoryDep, current_user: CurrentUserDep
):
    """Update an existing workflow."""
    wf = await repository.get_workflow_by_id(workflow_id)
    if not wf:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {workflow_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", workflow_id, details={"error_code": error_code})

    # Permission Check
    wf_org = wf.get("organization_id")
    is_system_wf = wf_org is None or wf_org == "system"

    if is_system_wf:
        if current_user.role != UserRole.ROOT:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_SYSTEM_WORKFLOW"
            logger.error(f"{error_code}: User {current_user.uid} tried modifying system workflow.", exc_info=True)
            raise PermissionDeniedError(message="Cannot modify system workflow", details={"error_code": error_code})
    else:
        # Tenant Workflow
        if current_user.role not in [UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER]:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_WORKFLOW_UPDATE"
            logger.error(f"{error_code}: User {current_user.uid} denied update.", exc_info=True)
            raise PermissionDeniedError(message="Permission denied", details={"error_code": error_code})
        if wf_org != current_user.organization_id and current_user.role != UserRole.ROOT:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_WORKFLOW_UPDATE"
            logger.error(
                f"{error_code}: Org mismatch (WF: {wf_org} vs User: {current_user.organization_id}).",
                exc_info=True,
            )
            raise PermissionDeniedError(message="Organization mismatch", details={"error_code": error_code})

    # Public Check
    if request.is_public is not None and request.is_public != wf.get("is_public"):
        if current_user.role != UserRole.ROOT:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_PUBLIC_VISIBILITY"
            logger.error(f"{error_code}: Non-ROOT user tried changing visibility.", exc_info=True)
            raise PermissionDeniedError(
                message="Public visibility restricted to ROOT", details={"error_code": error_code}
            )

    update_data: dict[str, Any] = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.description is not None:
        update_data["description"] = request.description
    if request.steps is not None:
        # Handle Nested Writes: Strings are IDs, Dicts are new/updated steps
        final_step_ids = []
        for s in request.steps:
            if isinstance(s, str):
                final_step_ids.append(s)
            elif isinstance(s, dict):
                # It's a step object.
                # 1. Extract ID
                s_id = s.get("id")
                if not s_id:
                    # Generate ID if missing (should imply new step)
                    s_id = f"step_{uuid.uuid4().hex[:8]}"
                    s["id"] = s_id
                
                final_step_ids.append(s_id)
                
                # 2. Save/Update Step Indepenently
                # We map the dict to our repository 'create_step' or 'update_step' logic.
                # Since we don't know if it exists, we try to get it first?
                # Or use an upsert method if available. Repository usually has update_step.
                # Note: This is "best effort" for now to fix the 422.
                # Ideally we validate the step schema (WorkflowStep) here.
                
                # Check existance
                existing_step = await repository.get_step_by_id(s_id)
                if existing_step:
                    # Update
                    # Filter out purely UI fields or map camelCase if needed?
                    # The frontend sends camelCase 'taskKey' but backend needs 'task_key'.
                    # We might need a quick mapper here or assume repository handles it.
                    # For now, pass 's' (update_data) directly.
                    await repository.update_step(s_id, s)
                else:
                    # Create
                    # Ensure minimal valid structure
                    if "name" not in s: s["name"] = "Untitled Step"
                    if "task_key" not in s and "taskKey" in s: s["task_key"] = s["taskKey"]
                    # If task_key is still missing, we might fail validation in repository.create_step
                    # if repository enforces it.
                    await repository.create_step(s)
                    
        update_data["steps"] = final_step_ids
    if request.ui_schema is not None:
        update_data["ui_schema"] = request.ui_schema
    if request.default_model_mapping is not None:
        update_data["default_model_mapping"] = request.default_model_mapping
    if request.is_public is not None:
        update_data["is_public"] = request.is_public
    if request.status is not None:
        update_data["status"] = request.status
    if request.version is not None:
        update_data["version"] = request.version
    if request.scoring_logic is not None:
        update_data["scoring_logic"] = request.scoring_logic

    update_data["updated_at"] = datetime.now()

    # Ensure Model Mapping Integrity
    final_steps = update_data.get("steps", wf.get("steps", []))
    final_mapping = update_data.get("default_model_mapping", wf.get("default_model_mapping", {})).copy()

    mapping_modified = False
    for s in final_steps:
        if s not in final_mapping:
            final_mapping[s] = "fast"
            mapping_modified = True

    if mapping_modified:
        # If input didn't provide mapping but we modified it based on steps, save it.
        update_data["default_model_mapping"] = final_mapping

    await repository.update_workflow(workflow_id, update_data)

    # Return Result with expanded steps
    result_wf = {**wf, **update_data}
    return await _expand_workflow(result_wf, repository)


@router.delete(
    "/workflows/{workflow_id}",
    summary="Delete Workflow",
    response_description="Deletion status and cleaned up orphans.",
)
async def delete_workflow(workflow_id: str, repository: RepositoryDep, current_user: CurrentUserDep):
    """Delete a workflow AND its orphan steps (Garbage Collection)."""
    wf = await repository.get_workflow_by_id(workflow_id)
    if not wf:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {workflow_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", workflow_id, details={"error_code": error_code})

    # Permission Check
    wf_org = wf.get("organization_id")
    is_system_wf = wf_org is None or wf_org == "system"

    if is_system_wf:
        if current_user.role != UserRole.ROOT:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_SYSTEM_WORKFLOW"
            logger.error(f"{error_code}: User {current_user.uid} tried deleting system workflow.", exc_info=True)
            raise PermissionDeniedError(message="Cannot delete system workflow", details={"error_code": error_code})
    else:
        if current_user.role not in [UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER]:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_WORKFLOW_DELETE"
            logger.error(f"{error_code}: User {current_user.uid} denied delete.", exc_info=True)
            raise PermissionDeniedError(message="Permission denied", details={"error_code": error_code})
        if wf_org != current_user.organization_id and current_user.role != UserRole.ROOT:
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_WORKFLOW_DELETE"
            logger.error(f"{error_code}: Org mismatch.", exc_info=True)
            raise PermissionDeniedError(message="Organization mismatch", details={"error_code": error_code})

    # 0. Integrity Check: Execution History
    all_execs = await repository.get_all_executions()
    related_execs = [e for e in all_execs if e.get("workflow_id") == workflow_id]

    if related_execs:
        error_code = "WORKFLOW_HAS_EXECUTIONS"
        logger.error(
            f"{error_code}: Workflow {workflow_id} has {len(related_execs)} executions. Deletion blocked.",
            exc_info=True,
        )
        from backend.exceptions import ConflictError

        raise ConflictError(
            message="Workflow has existing executions",
            details={"error_code": error_code, "execution_count": len(related_execs)},
        )

    # 1. Identify Orphan Steps
    orphans = []
    all_wfs = await repository.get_all_workflows()

    target_steps = set(wf.get("steps", []))
    used_elsewhere = set()
    for w in all_wfs:
        if w["id"] == workflow_id:
            continue
        for s in w.get("steps", []):
            used_elsewhere.add(s)
    orphans = list(target_steps - used_elsewhere)

    # 2. Delete Workflow
    await repository.delete_workflow(workflow_id)

    # 3. Delete Orphans
    deleted_steps = []
    for step_id in orphans:
        await repository.delete_step(step_id)
        deleted_steps.append(step_id)

    logger.info(f"Deleted workflow {workflow_id} and orphan steps: {deleted_steps}")

    return {"status": "deleted", "deleted_steps": deleted_steps}


@router.post("/workflows/{workflow_id}/copy", summary="Copy Workflow", response_description="The new workflow object.")
async def copy_workflow(workflow_id: str, request: CopyWorkflowRequest, repository: RepositoryDep):
    """Deep Copy a workflow structure (Shallow copy of steps)."""
    original = await repository.get_workflow_by_id(workflow_id)
    if not original:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {workflow_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", workflow_id, details={"error_code": error_code})

    new_id = f"{original['id']}_copy_{uuid.uuid4().hex[:4]}"

    new_wf = copy.deepcopy(original)
    new_wf["id"] = new_id
    new_wf["name"] = request.new_name
    new_wf["created_at"] = datetime.now()
    if "updated_at" in new_wf:
        del new_wf["updated_at"]

    clean_wf = dict(new_wf)

    try:
        await repository.create_workflow(clean_wf)
        return await _expand_workflow(clean_wf, repository)
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "WORKFLOW_COPY_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        ) from e
