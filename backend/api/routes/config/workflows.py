"""API Router for Workflows and Steps."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from tinydb import Query

from backend.dependencies import DatabaseDep, RegistryDep, RepositoryDep
from backend.services.validation_service import WorkflowValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["Configuration"])


# ... (Skipping Pydantic Models for brevity in replacement if possible, but simplest to replace block) ...
# Actually, I'll allow the models to remain and just target the endpoint block.
# I need to ensure RepositoryDep is imported. It wasn't in original imports.
# I will overwrite the imports section first? No, replace_file_content is better for chunks.

# I'll do this in two chunks or one large chunk if contiguous.
# Imports are at top. Endpoints are below.
# I will use multi_replace for safety.

# Chunk 1: Imports
# Chunk 2: Helper + Endpoints

# Wait, the tool is replace_file_content (single). 
# I will replace the imports line first, then the endpoints.
# Actually, I can just replace the whole file content or a large range? 
# The file is small enough (250 lines). 
# I will stick to targeting the specific function area.

# Let's adjust the imports first.
# Line 10: from backend.dependencies import DatabaseDep, RegistryDep


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["Configuration"])


class WorkflowUpdate(BaseModel):
    """Payload for updating a workflow."""

    steps: Annotated[list[dict[str, Any]] | None, Field(description="Complete list of step configurations.")] = None
    sequence: Annotated[list[str] | None, Field(description="Ordered list of step IDs.")] = None
    description: Annotated[str | None, Field(description="User-facing workflow description.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Map of StepID -> ModelStrategyKey.")] = (
        None
    )


class WorkflowCreate(BaseModel):
    """Payload for creating a new workflow."""

    id: Annotated[str, Field(description="New Workflow UUID/Slug.")]
    name: Annotated[str, Field(description="Workflow Name.")]
    sequence: Annotated[list[str], Field(description="List of Step IDs.")] = []
    description: Annotated[str | None, Field(description="Description.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Step-Model map.")] = {}


class StepCreate(BaseModel):
    """Payload for creating a step (generic dict wrapper for now)."""

    # Ideally should be strict Pydantic model but maintaining parity with original logic
    id: Annotated[str, Field(description="Step ID")]
    # Allowing extra fields
    model_config = {"extra": "allow"}

# --- STEPS ENDPOINTS ---


@router.get("/steps", summary="List Steps", response_description="All steps.")
def get_steps(db: DatabaseDep):
    """List all steps."""
    return db.table("steps").all()


@router.post("/steps", summary="Create Step", response_description="Created ID.")
def create_step(step: dict[str, Any], db: DatabaseDep):
    """Create a new step configuration."""
    table = db.table("steps")
    if table.search(Query().id == step.get("id")):
        from backend.exceptions import ConflictError

        error_code = "STEP_ID_EXISTS"
        logger.error(f"{error_code}: ID {step.get('id')}", exc_info=True)
        raise ConflictError(message="Resource conflict", details={"error_code": error_code})
    table.insert(step)
    return {"status": "created", "id": step.get("id")}


@router.put("/steps/{step_id}", summary="Update Step", response_description="Update status.")
def update_step(step_id: str, step: dict[str, Any], db: DatabaseDep):
    """Update a step configuration."""
    table = db.table("steps")
    if not table.search(Query().id == step_id):
        from backend.exceptions import ResourceNotFoundError

        error_code = "STEP_NOT_FOUND"
        logger.error(f"{error_code}: ID {step_id}", exc_info=True)
        raise ResourceNotFoundError("Step", step_id, details={"error_code": error_code})
    table.update(step, Query().id == step_id)
    return {"status": "updated", "id": step_id}


@router.delete("/steps/{step_id}", summary="Delete Step", response_description="Delete status.")
def delete_step(step_id: str, db: DatabaseDep):
    """Delete a step.

    Refactored to enforce Integrity: Cannot delete step if used in Workflows.
    """
    # 1. Check Existence
    table = db.table("steps")
    if not table.search(Query().id == step_id):
        from backend.exceptions import ResourceNotFoundError

        error_code = "STEP_NOT_FOUND"
        logger.error(f"{error_code}: ID {step_id}", exc_info=True)
        raise ResourceNotFoundError("Step", step_id, details={"error_code": error_code})

    # 2. Integrity Check: Workflow Usage
    workflows = db.table("workflows").all()
    used_in = []
    for wf in workflows:
        if step_id in wf.get("steps", []) or step_id in wf.get("sequence", []):
            used_in.append(wf.get("name", wf["id"]))

    if used_in:
        from backend.exceptions import ConflictError

        error_code = "STEP_IN_USE"
        logger.error(f"{error_code}: ID {step_id} used in {used_in}", exc_info=True)
        raise ConflictError(message="Resource conflict", details={"error_code": error_code, **{"used_in": used_in}})

    # 3. Delete
    table.remove(Query().id == step_id)
    return {"status": "deleted", "id": step_id}


# --- WORKFLOW ENDPOINTS ---



# --- HELPER: HYDRATION ---
async def _hydrate_workflow_steps(workflow_data: dict[str, Any], repository: Any) -> dict[str, Any]:
    """Hydrates workflow steps from the registry (SSOT)."""
    if not workflow_data.get("steps"):
        return workflow_data

    hydrated_steps = []

    for step in workflow_data["steps"]:
        # If it's a reference (dict with ID), try to hydrate
        step_id = step.get("id")
        if step_id:
            # 1. Fetch from Registry
            registry_step = await repository.get_step_by_id(step_id)
            
            if registry_step:
                # 2. Merge Logic: Registry Base + Workflow Overrides
                merged = registry_step.copy()
                
                # Overlay Workflow properties
                merged.update(step)
                
                # Special Case: Config
                if not step.get("config"):
                    merged["config"] = registry_step.get("config", {})
                else:
                    reg_config = registry_step.get("config", {})
                    wf_config = step.get("config", {})
                    final_config = reg_config.copy()
                    final_config.update(wf_config)
                    merged["config"] = final_config

                hydrated_steps.append(merged)
            else:
                # Registry missing? Keep as is
                hydrated_steps.append(step)
        else:
            hydrated_steps.append(step)

    workflow_data["steps"] = hydrated_steps
    return workflow_data


@router.get("/workflows", summary="List Workflows", response_description="All workflows.")
async def get_workflows(repository: RepositoryDep):
    """List all workflows."""
    workflows = await repository.get_all_workflows()
    # Hydrate all
    results = []
    for wf in workflows:
        results.append(await _hydrate_workflow_steps(wf, repository))
    return results


@router.get("/workflows/{wf_id}", summary="Get Workflow", response_description="Requested workflow.")
async def get_workflow(wf_id: str, repository: RepositoryDep):
    """Get a specific workflow."""
    wf = await repository.get_workflow_by_id(wf_id)
    if not wf:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": error_code})
    
    return await _hydrate_workflow_steps(wf, repository)


@router.put("/workflows/{wf_id}", summary="Update Workflow", response_description="Update status.")
def update_workflow(wf_id: str, update: WorkflowUpdate, db: DatabaseDep):
    """Update a workflow definition."""
    Workflow = Query()
    table = db.table("workflows")

    if not table.search(Workflow.id == wf_id):
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": error_code})

    update_data: dict[str, Any] = {}
    if update.steps is not None:
        update_data["steps"] = update.steps
    if update.sequence is not None:
        update_data["sequence"] = update.sequence
    if update.description:
        update_data["description"] = update.description
    if update.default_model_mapping is not None:
        update_data["default_model_mapping"] = update.default_model_mapping

    if not update_data:
        from backend.exceptions import AppException

        error_code = "NO_UPDATE_DATA"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        # Assuming 'e' was copy paste error in original, replacing with generic message
        raise AppException(
            message="No update data provided",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

    steps_to_check = update.steps if update.steps else update.sequence
    if steps_to_check:
        valid_steps = {s["id"] for s in db.table("steps").all()}
        for item in steps_to_check:
            sid = item if isinstance(item, str) else item.get("id")
            if sid and sid not in valid_steps:
                from backend.exceptions import AppException

                error_code = "INVALID_STEP_ID"
                logger.error(f"{error_code}: Step {sid} not found.", exc_info=True)
                raise AppException(
                    message=f"Step '{sid}' not found",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": error_code},
                )

    table.update(update_data, Workflow.id == wf_id)
    return {"status": "updated", "id": wf_id}


@router.post("/workflows", summary="Create Workflow", response_description="Created ID.")
def create_workflow(workflow: WorkflowCreate, db: DatabaseDep):
    """Create a new workflow."""
    Workflow = Query()
    table = db.table("workflows")

    if table.search(Workflow.id == workflow.id):
        from backend.exceptions import ConflictError

        error_code = "WORKFLOW_ID_EXISTS"
        logger.error(f"{error_code}: ID {workflow.id}", exc_info=True)
        raise ConflictError(message="Resource conflict", details={"error_code": error_code})

    new_wf = workflow.model_dump()
    if workflow.sequence:
        valid_steps = {s["id"] for s in db.table("steps").all()}
        for step_id in workflow.sequence:
            if step_id not in valid_steps:
                from backend.exceptions import AppException

                error_code = "INVALID_STEP_ID"
                logger.error(f"{error_code}: Step {step_id} not found.", exc_info=True)
                raise AppException(
                    message=f"Step '{step_id}' not found",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": error_code},
                )

    table.insert(new_wf)
    return {"status": "created", "id": workflow.id}


@router.delete("/workflows/{wf_id}", summary="Delete Workflow", response_description="Delete status.")
def delete_workflow(wf_id: str, db: DatabaseDep):
    """Delete a workflow."""
    Workflow = Query()
    table = db.table("workflows")
    if not table.search(Workflow.id == wf_id):
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": error_code})
    table.remove(Workflow.id == wf_id)
    return {"status": "deleted", "id": wf_id}


@router.post("/validate-flow", summary="Validate Flow", response_description="Validation Report.")
async def validate_flow(workflow: WorkflowCreate, db: DatabaseDep, registry: RegistryDep):
    """Dry run validation."""
    all_steps_config = db.table("steps").all()
    steps_db_map = {s["id"]: s for s in all_steps_config}

    return await WorkflowValidator.validate_flow_configuration(
        sequence=workflow.sequence,
        steps_db_map=steps_db_map,
        registry=registry,
    )
