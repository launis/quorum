"""Builder Steps Routes.

Handles step listing, details, and customization endpoints.
"""

import copy
import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Body, status
from pydantic import BaseModel, Field

from backend.dependencies import RepositoryDep

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---

class StepUpdateRequest(BaseModel):
    """Payload for updating a step configuration."""

    name: Annotated[str | None, Field(description="New step name.")] = None
    execution_config: Annotated[dict[str, Any] | None, Field(description="Updated execution config.")] = None


class CustomStepCreateRequest(BaseModel):
    """Payload for creating a custom step."""

    component_type: Annotated[str, Field(description="Base component type (e.g. 'Judge', 'Analyst').")]
    name_hint: Annotated[str | None, Field(description="Optional name override.")] = None

# --- Endpoints ---

@router.get("/steps", summary="List Steps", response_description="All Steps.")
async def list_steps(repository: RepositoryDep):
    """List all available steps."""
    return await repository.get_all_steps()


@router.get("/steps/{step_id}", summary="Get Step Details", response_description="Step configuration.")
async def get_step_details(step_id: str, repository: RepositoryDep):
    """V2: Get full configuration of a step."""
    step = await repository.get_step_by_id(step_id)
    if not step:
        from backend.exceptions import ResourceNotFoundError

        error_code = "STEP_NOT_FOUND"
        logger.error(f"{error_code}: ID {step_id}", exc_info=True)
        raise ResourceNotFoundError("Step", step_id, details={"error_code": error_code})
    return step


@router.put("/steps/{step_id}", summary="Update Step", response_description="Updated step.")
async def update_step(step_id: str, request: StepUpdateRequest, repository: RepositoryDep):
    """V2: Update a step configuration.

    WARNING: This modifies the global step definition.
    """
    step = await repository.get_step_by_id(step_id)
    if not step:
        from backend.exceptions import ResourceNotFoundError

        error_code = "STEP_NOT_FOUND"
        logger.error(f"{error_code}: ID {step_id}", exc_info=True)
        raise ResourceNotFoundError("Step", step_id, details={"error_code": error_code})

    update_data: dict[str, Any] = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.execution_config is not None:
        update_data["execution_config"] = request.execution_config

    await repository.update_step(step_id, update_data)

    return {**step, **update_data}


@router.post("/steps/clone", summary="Clone Step", response_description="The new custom step config.")
async def clone_step(repository: RepositoryDep, source_step_id: str = Body(..., embed=True)):
    """V2: Clone a step to a new Custom Step (Copy-on-Write)."""
    step = await repository.get_step_by_id(source_step_id)
    if not step:
        from backend.exceptions import ResourceNotFoundError

        error_code = "SOURCE_STEP_NOT_FOUND"
        logger.error(f"{error_code}: ID {source_step_id}", exc_info=True)
        raise ResourceNotFoundError("Step", source_step_id, details={"error_code": error_code})

    new_id = f"{source_step_id}_custom_{uuid.uuid4().hex[:6]}"
    new_step = copy.deepcopy(step)
    new_step["id"] = new_id
    new_step["name"] = f"{step.get('name')} (Custom)"

    clean_step = dict(new_step)

    await repository.create_step(clean_step)

    return clean_step


@router.post(
    "/steps/create-custom",
    summary="Create Custom Step",
    response_description="The newly created custom step.",
)
async def create_custom_step(req: CustomStepCreateRequest, repository: RepositoryDep):
    """Creates a new custom step definition server-side with proper defaults."""
    # 1. Generate ID
    prefix = f"custom_{req.component_type.lower()}"
    new_id = f"{prefix}_{uuid.uuid4().hex[:6]}"

    # 2. Determine Defaults based on Component Type
    # Heuristic defaults for known agents
    prompts = []
    if "Judge" in req.component_type:
        prompts = ["TASK_JUDGE", "GLOBAL_CONTEXT"]
    elif "Reporter" in req.component_type:
        prompts = ["TASK_REPORT"]

    execution_config = {"llm_prompts": prompts}

    # 3. Construct Payload
    name = req.name_hint or f"Custom {req.component_type} Step"

    new_step = {
        "id": new_id,
        "name": name,
        "component": req.component_type,
        "description": "Created via Workflow Builder",
        "execution_config": execution_config,
        "output_config_component": None,
        "output_filename": f"{new_id}.json",
        "is_custom": True,
    }

    # 4. Save
    try:
        await repository.create_step(new_step)
        return new_step
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "CUSTOM_STEP_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        ) from e


@router.get("/utils/generate-id", summary="Generate ID", response_description="A unique ID string.")
async def generate_id(prefix: str = "custom_step"):
    """Generates a unique ID with optional prefix."""
    return {"id": f"{prefix}_{uuid.uuid4().hex[:6]}"}
