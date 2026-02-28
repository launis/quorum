"""API Router for Configuration Steps."""

import logging

from fastapi import APIRouter
from tinydb import Query

from backend.dependencies import DatabaseDep
from backend.exceptions import AppException, ConflictError, ErrorCodes, ResourceNotFoundError, format_validation_error
from backend.models.dtos.config import StepDefinition, StepDeleteResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Configuration"])


# --- Routes ---


@router.get("", summary="List Steps", response_description="All steps.", response_model=list[StepDefinition])
def get_steps(db: DatabaseDep) -> list[StepDefinition]:
    """Retrieves all defined steps. Pydantic model handles adaptation automatically."""
    try:
        steps = db.table("steps").all()
        return [StepDefinition(**s) for s in steps]
    except Exception as e:
        error_code = ErrorCodes.STEP_LIST_FAILED
        logger.error(f"[StepsRoute] {error_code}: {e}", exc_info=True)
        raise AppException(message=format_validation_error(e), status_code=500, details={"error_code": error_code}) from e


@router.get("/{step_id}", summary="Get Step", response_model=StepDefinition)
def get_step(step_id: str, db: DatabaseDep) -> StepDefinition:
    """Retrieves a single step by ID."""
    try:
        Step = Query()
        doc = db.table("steps").get(Step.id == step_id)
        if not doc:
            raise ResourceNotFoundError(resource_type="Step", resource_id=step_id)
        return StepDefinition(**doc)
    except Exception as e:
        if isinstance(e, ResourceNotFoundError):
            raise e

        error_code = ErrorCodes.STEP_FETCH_FAILED
        logger.error(f"[StepsRoute] {error_code}: {e}", exc_info=True)
        raise AppException(message=format_validation_error(e), status_code=500, details={"error_code": error_code}) from e


@router.post("", summary="Create Step", response_description="Status and ID.", response_model=StepDefinition)
def create_step(step: StepDefinition, db: DatabaseDep) -> StepDefinition:
    """Creates a new step. Pydantic validator adapts legacy input to DB schema."""
    try:
        table = db.table("steps")
        Step = Query()

        if table.search(Step.id == step.id):
            raise ConflictError(message="Step ID already exists", details={"id": step.id})

        # Dump passing 'exclude' for computed fields to store only raw DB types
        # Actually, exclude={'component', 'execution_config'} is needed if we don't want them in DB.
        # But computed_fields are usually read-only.
        # We explicitly verify what we store.
        doc = step.model_dump(exclude={"component", "execution_config"})
        table.insert(doc)
        return step
    except Exception as e:
        if isinstance(e, ConflictError):
            raise e

        error_code = ErrorCodes.STEP_CREATE_FAILED
        logger.error(f"[StepsRoute] {error_code}: {e}", exc_info=True)
        raise AppException(message=format_validation_error(e), status_code=500, details={"error_code": error_code}) from e


@router.put("/{step_id}", summary="Update Step", response_model=StepDefinition)
def update_step(step_id: str, step: StepDefinition, db: DatabaseDep) -> StepDefinition:
    """Updates an existing step."""
    try:
        table = db.table("steps")
        Step = Query()

        # Check existence
        if not table.contains(Step.id == step_id):
            raise ResourceNotFoundError(resource_type="Step", resource_id=step_id)

        # Prevent ID change collision
        if step.id != step_id and table.contains(Step.id == step.id):
            raise ConflictError(message="New Step ID already exists", details={"id": step.id})

        # Prepare Doc (Exclude computed legacy fields from DB)
        doc = step.model_dump(exclude={"component", "execution_config"})

        # Update logic
        if step.id == step_id:
            table.update(doc, Step.id == step_id)
        else:
            table.remove(Step.id == step_id)
            table.insert(doc)

        return step
    except Exception as e:
        if isinstance(e, (ResourceNotFoundError, ConflictError)):
            raise e

        error_code = ErrorCodes.STEP_UPDATE_FAILED
        logger.error(f"[StepsRoute] {error_code}: {e}", exc_info=True)
        raise AppException(message=format_validation_error(e), status_code=500, details={"error_code": error_code}) from e


@router.delete("/{step_id}", summary="Delete Step", response_model=StepDeleteResponse)
def delete_step(step_id: str, db: DatabaseDep) -> StepDeleteResponse:
    """Deletes a step."""
    try:
        table = db.table("steps")
        Step = Query()

        if not table.contains(Step.id == step_id):
            raise ResourceNotFoundError(resource_type="Step", resource_id=step_id)

        table.remove(Step.id == step_id)
        return StepDeleteResponse(status="deleted", id=step_id)
    except Exception as e:
        if isinstance(e, ResourceNotFoundError):
            raise e

        error_code = ErrorCodes.STEP_DELETE_FAILED
        logger.error(f"[StepsRoute] {error_code}: {e}", exc_info=True)
        raise AppException(message=format_validation_error(e), status_code=500, details={"error_code": error_code}) from e
