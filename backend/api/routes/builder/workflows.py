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


class WorkflowUpdateRequest(BaseModel):
    """Payload for updating an existing workflow."""
    name: Annotated[str | None, Field(description="New name.")] = None
    description: Annotated[str | None, Field(description="New description.")] = None
    steps: Annotated[list[str] | None, Field(description="New step sequence.")] = None
    ui_schema: Annotated[dict[str, Any] | None, Field(description="New UI metadata.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Updated model mapping.")] = None
    is_public: Annotated[bool | None, Field(description="Update visibility.")] = None
    status: Annotated[str | None, Field(description="Update status.")] = None
    version: Annotated[int | None, Field(description="Update version.")] = None


class CopyWorkflowRequest(BaseModel):
    """Payload for copying a workflow."""
    new_name: Annotated[str, Field(description="Name for the copy.")]

# --- Endpoints ---

@router.get("/workflows", summary="List Workflows", response_description="All Workflows.")
async def list_workflows(repository: RepositoryDep, current_user: CurrentUserDep):
    """List all workflows visible to the current user."""
    return await repository.get_all_workflows(organization_id=current_user.organization_id, role=current_user.role)


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
        }

        await repository.create_workflow(workflow_data)
        return workflow_data
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
    wf = await repository.get_workflow_by_id(workflow_id)
    if not wf:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {workflow_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", workflow_id, details={"error_code": error_code})
    return wf


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
        update_data["steps"] = request.steps
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

    return {**wf, **update_data}


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
        return clean_wf
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "WORKFLOW_COPY_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        ) from e
