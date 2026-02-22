"""Builder Workflow Routes.

Handles Creation, Update, Deletion, and Listing of Workflows.
"""

import copy
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, status

from backend.dependencies import CurrentUserDep, PromptBuilderDep, RepositoryDep
from backend.models.auth import UserRole

router = APIRouter()
from backend.models.dtos.builder import (
    BuilderWorkflowCreateRequest,
    ChainPreviewResponse,
    CopyWorkflowRequest,
    WorkflowDeleteResponse,
    WorkflowResponse,
    WorkflowUpdateRequest,
)

logger = logging.getLogger(__name__)


# --- Helpers ---


async def _expand_workflow(wf: dict[str, Any], repository: RepositoryDep) -> dict[str, Any]:
    """Hydrates step IDs into full step objects using SSOT Registry.
    Hyper-Strict Mode: Only pure string IDs are permitted in the workflow.
    """
    full_wf = wf.copy()
    step_ids = wf.get("steps", [])

    hydrated_steps = []
    # Hyper-Strict: step_ids is strictly list[str]
    for step_id in step_ids:
        if not isinstance(step_id, str):
            continue

        # Fetch Canonical Definition from Registry (SSOT)
        canonical_step = await repository.get_step_by_id(step_id)

        if canonical_step:
            # We copy canonical to avoid mutating cache/db result
            merged = canonical_step.copy()

            # Ensure 'task_key' exists for frontend strict parsing
            if "task_key" not in merged:
                merged["task_key"] = merged.get("component", "unknown")

            hydrated_steps.append(merged)
        else:
            # Fallback for missing registry component to prevent Frontend Crash
            logger.warning(
                f"\n[ORPHANED STEP DETECTED] Workflow: '{wf.get('name', 'Unknown')}' (ID: {wf.get('id')})\n"
                f"└── Missing Step ID: '{step_id}'\n"
                f"└── Action Required: Open this workflow in Cognitive Studio. The missing step will be highlighted in red. "
                f"Delete it from the workflow graph or restore the step definition to your database."
            )
            hydrated_steps.append(
                {"id": step_id, "name": f"Missing Step ({step_id})", "task_key": "unknown", "is_missing_registry": True}
            )

    full_wf["steps"] = hydrated_steps
    return full_wf


# --- Endpoints ---


@router.get(
    "/workflows", summary="List Workflows", response_description="All Workflows.", response_model=list[WorkflowResponse]
)
async def list_workflows(repository: RepositoryDep, current_user: CurrentUserDep) -> list[WorkflowResponse]:
    """List all workflows visible to the current user."""
    raw_wfs = await repository.get_all_workflows(organization_id=current_user.organization_id, role=current_user.role)
    expanded = [await _expand_workflow(wf, repository) for wf in raw_wfs]
    return [WorkflowResponse(**wf) for wf in expanded]


@router.post(
    "/workflows",
    summary="Create Workflow",
    response_description="Created workflow data.",
    response_model=WorkflowResponse,
)
async def create_workflow(
    request: BuilderWorkflowCreateRequest, repository: RepositoryDep, current_user: CurrentUserDep
) -> WorkflowResponse:
    """Create a new workflow."""
    # 1. RBAC Check
    if current_user.role not in [UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER]:
        from backend.exceptions import PermissionDeniedError

        error_code = "PERMISSION_DENIED_WORKFLOW_CREATE"
        logger.error(f"{error_code}: User {current_user.uid} (Role {current_user.role}) denied.", exc_info=True)
        raise PermissionDeniedError(message="Permission denied", details={"error_code": error_code})

    # 2. Org Assignment
    target_org = current_user.organization_id
    if not target_org:
        from backend.exceptions import AppException

        error_code = "WORKFLOW_MISSING_ORGANIZATION_ID"
        logger.error(f"{error_code}: User {current_user.uid} has no organization_id assigned.", exc_info=True)
        raise AppException(
            message="User must belong to an organization to create workflows.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

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

    # 4. Strict Model Mapping Validation
    # Identify all step IDs referenced in the request
    requested_step_ids = set()
    for s in request.steps:
        if isinstance(s, str):
            requested_step_ids.add(s)
        elif isinstance(s, dict):
            if "id" in s:
                requested_step_ids.add(s["id"])
            # If dict has no ID, strict validation might fail or we assume it's created later.
            # However, mapping requires IDs. If ID is missing here, it can't be mapped.
            # But create_workflow doesn't generate IDs for steps currently (unlike update).
            # We assume client provides IDs or references.

    mapped_steps = set(request.default_model_mapping.keys()) if request.default_model_mapping else set()

    missing_mapping = requested_step_ids - mapped_steps
    if missing_mapping:
        from backend.exceptions import AppException

        error_code = "WORKFLOW_MISSING_MODEL_MAPPING"
        logger.error(f"{error_code}: Steps {missing_mapping} missing from model mapping.")
        raise AppException(
            message=f"Strict Mode: Missing model mapping for steps: {list(missing_mapping)}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code, "missing_steps": list(missing_mapping)},
        )

    try:
        new_id = str(uuid.uuid4()).split("-")[0]  # Short ID
        workflow_data = {
            "id": f"wf_{new_id}",
            "name": request.name,
            "description": request.description or "",
            "steps": request.steps,
            "default_model_mapping": request.default_model_mapping or {},
            "ui_schema": request.ui_schema or {},
            "created_at": datetime.now(UTC),
            "organization_id": target_org,
            "is_public": is_public_val,
            "status": request.status,
            "version": request.version,
            "scoring_logic": request.scoring_logic,
        }

        await repository.create_workflow(workflow_data)

        # Return expanded
        expanded = await _expand_workflow(workflow_data, repository)
        return WorkflowResponse(**expanded)
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "WORKFLOW_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.get(
    "/workflows/{workflow_id}",
    summary="Get Workflow",
    response_description="Workflow details.",
    response_model=WorkflowResponse,
)
async def get_workflow(workflow_id: str, repository: RepositoryDep) -> WorkflowResponse:
    """Get details of a specific workflow."""
    logger.info(f"GET Workflow Request. ID: '{workflow_id}'")
    wf = await repository.get_workflow_by_id(workflow_id)
    if not wf:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID '{workflow_id}' not found in Repository. Type: {type(workflow_id)}")
        raise ResourceNotFoundError("Workflow", workflow_id, details={"error_code": error_code})
    logger.info(f"Found workflow: {wf.get('id')} - {wf.get('name')}")

    expanded = await _expand_workflow(wf, repository)
    return WorkflowResponse(**expanded)


@router.put(
    "/workflows/{workflow_id}",
    summary="Update Workflow",
    response_description="Updated workflow.",
    response_model=WorkflowResponse,
)
async def update_workflow(
    workflow_id: str, request: WorkflowUpdateRequest, repository: RepositoryDep, current_user: CurrentUserDep
) -> WorkflowResponse:
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

    try:
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
                    # Note: This is "best effort" for now to fix the 422.

                    # Check existance
                    existing_step = await repository.get_step_by_id(s_id)
                    if existing_step:
                        # Update
                        await repository.update_step(s_id, s)
                    else:
                        # Create
                        # Ensure minimal valid structure
                        if "name" not in s:
                            s["name"] = "Untitled Step"
                        if "task_key" not in s and "taskKey" in s:
                            s["task_key"] = s["taskKey"]
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

        update_data["updated_at"] = datetime.now(UTC)

        # Ensure Model Mapping Integrity
        final_steps = update_data.get("steps", wf.get("steps", []))
        final_mapping = update_data.get("default_model_mapping", wf.get("default_model_mapping", {})).copy()

        # Strict Validation: All steps MUST have a mapping
        final_step_id_set = set(final_steps)  # Assuming list of strings (IDs) at this point
        mapped_step_ids = set(final_mapping.keys())

        missing_mapping = final_step_id_set - mapped_step_ids
        if missing_mapping:
            from backend.exceptions import AppException

            error_code = "WORKFLOW_MISSING_MODEL_MAPPING"
            logger.error(f"{error_code}: Steps {missing_mapping} missing from model mapping (Update).")
            raise AppException(
                message=f"Strict Mode: Missing model mapping for steps: {list(missing_mapping)}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": error_code, "missing_steps": list(missing_mapping)},
            )

        await repository.update_workflow(workflow_id, update_data)

        # Return Result with expanded steps
        result_wf = {**wf, **update_data}
        expanded = await _expand_workflow(result_wf, repository)
        return WorkflowResponse(**expanded)

    except Exception as e:
        from backend.exceptions import AppException

        # Allow specialized exceptions to bubble up if already raised
        if isinstance(e, AppException):
            raise e

        error_code = "WORKFLOW_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.delete(
    "/workflows/{workflow_id}",
    summary="Delete Workflow",
    response_description="Deletion status and cleaned up orphans.",
    response_model=WorkflowDeleteResponse,
)
async def delete_workflow(
    workflow_id: str, repository: RepositoryDep, current_user: CurrentUserDep
) -> WorkflowDeleteResponse:
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
    try:
        all_execs = await repository.get_all_executions()
        related_execs = [e for e in all_execs if getattr(e, "workflow_id", None) == workflow_id]

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

        return WorkflowDeleteResponse(status="deleted", deleted_steps=deleted_steps)

    except Exception as e:
        from backend.exceptions import AppException

        if isinstance(e, AppException):
            raise e

        error_code = "WORKFLOW_DELETION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.post(
    "/workflows/{workflow_id}/copy",
    summary="Copy Workflow",
    response_description="The new workflow object.",
    response_model=WorkflowResponse,
)
async def copy_workflow(workflow_id: str, request: CopyWorkflowRequest, repository: RepositoryDep) -> WorkflowResponse:
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
    new_wf["created_at"] = datetime.now(UTC)
    if "updated_at" in new_wf:
        del new_wf["updated_at"]

    clean_wf = dict(new_wf)

    try:
        await repository.create_workflow(clean_wf)
        expanded = await _expand_workflow(clean_wf, repository)
        return WorkflowResponse(**expanded)
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "WORKFLOW_COPY_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        ) from e


@router.get(
    "/workflows/{workflow_id}/chain-preview",
    summary="Preview Full Chain",
    response_description="Markdown content of the full chain.",
    response_model=ChainPreviewResponse,
)
async def preview_chain(
    workflow_id: str, repository: RepositoryDep, prompt_builder: PromptBuilderDep
) -> ChainPreviewResponse:
    """Generates a markdown preview of the entire workflow chain."""
    logger.info(f"Generating chain preview for workflow: {workflow_id}")
    try:
        content = await prompt_builder.preview_full_chain_prompts(workflow_id)
        return ChainPreviewResponse(markdown_content=content)
    except Exception as e:
        from backend.exceptions import AppException, ResourceNotFoundError

        if "not found" in str(e).lower():
            raise ResourceNotFoundError("Workflow", workflow_id)

        error_code = "CHAIN_PREVIEW_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e
