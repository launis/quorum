"""API Router for Workflows and Steps."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from tinydb import Query

from backend.dependencies import DatabaseDep, RegistryDep, RepositoryDep
from backend.services.localization import localize_schema
from backend.services.validation_service import WorkflowValidator
from backend.exceptions import ConflictError, ResourceNotFoundError, AppException
from backend.models.dtos.config import (
    StepDefinition,
    StepDeleteResponse,
    WorkflowConfigDefinition,
    WorkflowConfigCreate,
    WorkflowConfigUpdate,
    WorkflowDeleteResponse,
    ValidationReportResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Configuration"])

# --- STEPS ENDPOINTS ---


@router.get("/steps", summary="List Steps", response_description="All steps.", response_model=list[StepDefinition])
def get_steps(db: DatabaseDep) -> list[StepDefinition]:
    """List all steps."""
    try:
        steps = db.table("steps").all()
        return [StepDefinition(**s) for s in steps]
    except Exception as e:
        error_code = "STEP_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.post("/steps", summary="Create Step", response_description="Created ID.", response_model=StepDefinition)
def create_step(step: StepDefinition, db: DatabaseDep) -> StepDefinition:
    """Create a new step configuration."""
    try:
        table = db.table("steps")
        if table.search(Query().id == step.id):
            raise ConflictError(message="Resource conflict", details={"error_code": "STEP_ID_EXISTS"})
        
        doc = step.model_dump(exclude={'component', 'execution_config'})
        table.insert(doc)
        return step
    except Exception as e:
        if isinstance(e, ConflictError):
             raise e
        
        error_code = "STEP_CREATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.put("/steps/{step_id}", summary="Update Step", response_description="Update status.", response_model=StepDefinition)
def update_step(step_id: str, step: StepDefinition, db: DatabaseDep) -> StepDefinition:
    """Update a step configuration."""
    try:
        table = db.table("steps")
        if not table.search(Query().id == step_id):
            raise ResourceNotFoundError("Step", step_id, details={"error_code": "STEP_NOT_FOUND"})
        
        # Prevent ID change collision
        if step.id != step_id and table.contains(Query().id == step.id):
             raise ConflictError(message="New Step ID already exists", details={"id": step.id})

        doc = step.model_dump(exclude={'component', 'execution_config'})
        
        if step.id == step_id:
            table.update(doc, Query().id == step_id)
        else:
            table.remove(Query().id == step_id)
            table.insert(doc)
            
        return step
    except Exception as e:
         if isinstance(e, (ResourceNotFoundError, ConflictError)):
             raise e
         
         error_code = "STEP_UPDATE_FAILED"
         logger.error(f"{error_code}: {e}", exc_info=True)
         raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
         ) from e


@router.delete("/steps/{step_id}", summary="Delete Step", response_description="Delete status.", response_model=StepDeleteResponse)
def delete_step(step_id: str, db: DatabaseDep) -> StepDeleteResponse:
    """Delete a step.

    Refactored to enforce Integrity: Cannot delete step if used in Workflows.
    """
    try:
        # 1. Check Existence
        table = db.table("steps")
        if not table.search(Query().id == step_id):
            raise ResourceNotFoundError("Step", step_id, details={"error_code": "STEP_NOT_FOUND"})

        # 2. Integrity Check: Workflow Usage
        workflows = db.table("workflows").all()
        used_in = []
        for wf in workflows:
            if step_id in wf.get("steps", []) or step_id in wf.get("sequence", []):
                used_in.append(wf.get("name", wf["id"]))

        if used_in:
            raise ConflictError(message="Resource conflict", details={"error_code": "STEP_IN_USE", "used_in": used_in})

        # 3. Delete
        table.remove(Query().id == step_id)
        return StepDeleteResponse(status="deleted", id=step_id)
    except Exception as e:
         if isinstance(e, (ResourceNotFoundError, ConflictError)):
             raise e
         
         error_code = "STEP_DELETE_FAILED"
         logger.error(f"{error_code}: {e}", exc_info=True)
         raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
         ) from e


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


@router.get("", summary="List Workflows", response_description="All workflows.", response_model=list[WorkflowConfigDefinition])
async def get_workflows(repository: RepositoryDep) -> list[WorkflowConfigDefinition]:
    """List all workflows."""
    try:
        workflows = await repository.get_all_workflows()
        # Hydrate all
        results = []
        for wf in workflows:
            hydrated = await _hydrate_workflow_steps(wf, repository)
            # Localize UI Schema (Dynamic Input Form)
            if "ui_schema" in hydrated and isinstance(hydrated["ui_schema"], dict):
                hydrated["ui_schema"] = localize_schema(hydrated["ui_schema"])
            results.append(WorkflowConfigDefinition(**hydrated))
        return results
    except Exception as e:
        error_code = "WORKFLOW_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.get("/{wf_id}", summary="Get Workflow", response_description="Requested workflow.", response_model=WorkflowConfigDefinition)
async def get_workflow(wf_id: str, repository: RepositoryDep) -> WorkflowConfigDefinition:
    """Get a specific workflow."""
    try:
        wf = await repository.get_workflow_by_id(wf_id)
        if not wf:
            raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": "WORKFLOW_NOT_FOUND"})

        hydrated = await _hydrate_workflow_steps(wf, repository)

        # Localize UI Schema
        if "ui_schema" in hydrated and isinstance(hydrated["ui_schema"], dict):
            hydrated["ui_schema"] = localize_schema(hydrated["ui_schema"])

        return WorkflowConfigDefinition(**hydrated)
    except Exception as e:
        if isinstance(e, ResourceNotFoundError):
             raise e
        
        error_code = "WORKFLOW_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.put("/{wf_id}", summary="Update Workflow", response_description="Update status.", response_model=WorkflowConfigDefinition)
def update_workflow(wf_id: str, update: WorkflowConfigUpdate, db: DatabaseDep) -> WorkflowConfigDefinition:
    """Update a workflow definition."""
    try:
        Workflow = Query()
        table = db.table("workflows")

        if not table.search(Workflow.id == wf_id):
            raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": "WORKFLOW_NOT_FOUND"})

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
            raise AppException(
                message="No update data provided",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": "NO_UPDATE_DATA"},
            )

        steps_to_check = update.steps if update.steps else update.sequence
        if steps_to_check:
            valid_steps = {s["id"] for s in db.table("steps").all()}
            for item in steps_to_check:
                sid = item if isinstance(item, str) else item.get("id")
                if sid and sid not in valid_steps:
                    raise AppException(
                        message=f"Step '{sid}' not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_STEP_ID"},
                    )

        table.update(update_data, Workflow.id == wf_id)
        # Fetch updated to return full object
        updated_doc = table.get(Workflow.id == wf_id)
        return WorkflowConfigDefinition(**updated_doc)
    except Exception as e:
        if isinstance(e, (ResourceNotFoundError, AppException)):
             raise e
        
        error_code = "WORKFLOW_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.post("", summary="Create Workflow", response_description="Created ID.", response_model=WorkflowConfigDefinition)
def create_workflow(workflow: WorkflowConfigCreate, db: DatabaseDep) -> WorkflowConfigDefinition:
    """Create a new workflow."""
    try:
        Workflow = Query()
        table = db.table("workflows")

        if table.search(Workflow.id == workflow.id):
            raise ConflictError(message="Resource conflict", details={"error_code": "WORKFLOW_ID_EXISTS"})

        new_wf = workflow.model_dump()
        if workflow.sequence:
            valid_steps = {s["id"] for s in db.table("steps").all()}
            for step_id in workflow.sequence:
                if step_id not in valid_steps:
                    raise AppException(
                        message=f"Step '{step_id}' not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_STEP_ID"},
                    )

        table.insert(new_wf)
        return WorkflowConfigDefinition(**new_wf)
    except Exception as e:
        if isinstance(e, (ConflictError, AppException)):
             raise e
        
        error_code = "WORKFLOW_CREATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.delete("/{wf_id}", summary="Delete Workflow", response_description="Delete status.", response_model=WorkflowDeleteResponse)
def delete_workflow(wf_id: str, db: DatabaseDep) -> WorkflowDeleteResponse:
    """Delete a workflow."""
    try:
        Workflow = Query()
        table = db.table("workflows")
        if not table.search(Workflow.id == wf_id):
            raise ResourceNotFoundError("Workflow", wf_id, details={"error_code": "WORKFLOW_NOT_FOUND"})
        table.remove(Workflow.id == wf_id)
        return WorkflowDeleteResponse(status="deleted", id=wf_id)
    except Exception as e:
        if isinstance(e, ResourceNotFoundError):
             raise e
        
        error_code = "WORKFLOW_DELETE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.post("/validate-flow", summary="Validate Flow", response_description="Validation Report.", response_model=ValidationReportResponse)
async def validate_flow(workflow: WorkflowConfigCreate, db: DatabaseDep, registry: RegistryDep) -> ValidationReportResponse:
    """Dry run validation."""
    try:
        all_steps_config = db.table("steps").all()
        steps_db_map = {s["id"]: s for s in all_steps_config}

        report = await WorkflowValidator.validate_flow_configuration(
            sequence=workflow.sequence,
            steps_db_map=steps_db_map,
            registry=registry,
        )
        return ValidationReportResponse(**report)
    except Exception as e:
        error_code = "WORKFLOW_VALIDATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e
