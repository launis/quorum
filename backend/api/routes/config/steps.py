"""API Router for Configuration Steps."""

import logging
from typing import Annotated, Any, List

from fastapi import APIRouter, Path, Body
from pydantic import BaseModel, Field
from tinydb import Query

from backend.dependencies import DatabaseDep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["Configuration"])


# --- Models ---

class StepConfig(BaseModel):
    """
    Step Configuration (Direct DB Mapping).
    """
    id: str = Field(..., description="Unique step identifier", json_schema_extra={"x-ui-label": "Step ID"})
    name: str = Field(..., description="Human-readable name", json_schema_extra={"x-ui-label": "Nimi"})
    description: str | None = Field(None, json_schema_extra={"x-ui-label": "Kuvaus"})
    
    # Primary DB Fields
    task_key: str = Field("analyst", description="Task Key (DB source)", json_schema_extra={"x-ui-label": "Agentti"})
    config: dict[str, Any] = Field(default_factory=dict, description="Configuration (DB source)", json_schema_extra={"x-ui-label": "Asetukset"})


# --- Routes ---

@router.get("/steps", summary="List Steps", response_description="All steps.", response_model=List[StepConfig])
def get_steps(db: DatabaseDep):
    "Retrieves all defined steps. Pydantic model handles adaptation automatically."
    return db.table("steps").all()


@router.get("/steps/{step_id}", summary="Get Step", response_model=StepConfig)
def get_step(step_id: str, db: DatabaseDep):
    "Retrieves a single step by ID."
    Step = Query()
    doc = db.table("steps").get(Step.id == step_id)
    if not doc:
        raise ResourceNotFoundError(message=f"Step '{step_id}' not found.")
    return doc


@router.post("/steps", summary="Create Step", response_description="Status and ID.")
def create_step(step: StepConfig, db: DatabaseDep):
    "Creates a new step. Pydantic validator adapts legacy input to DB schema."
    table = db.table("steps")
    Step = Query()
    
    if table.search(Step.id == step.id):
        raise ConflictError(message="Step ID already exists", details={"id": step.id})

    # Dump passing 'exclude' for computed fields to store only raw DB types
    # Actually, exclude={'component', 'execution_config'} is needed if we don't want them in DB.
    # But computed_fields are usually read-only.
    # We explicitly verify what we store.
    doc = step.model_dump(exclude={'component', 'execution_config'})
    table.insert(doc)
    return {"status": "created", "id": step.id}


@router.put("/steps/{step_id}", summary="Update Step")
def update_step(step_id: str, step: StepConfig, db: DatabaseDep):
    "Updates an existing step."
    table = db.table("steps")
    Step = Query()
    
    # Check existence
    if not table.contains(Step.id == step_id):
         raise ResourceNotFoundError(message=f"Step '{step_id}' not found.")

    # Prevent ID change collision
    if step.id != step_id and table.contains(Step.id == step.id):
         raise ConflictError(message="New Step ID already exists", details={"id": step.id})

    # Prepare Doc (Exclude computed legacy fields from DB)
    doc = step.model_dump(exclude={'component', 'execution_config'})
    
    # Update logic
    if step.id == step_id:
        table.update(doc, Step.id == step_id)
    else:
        table.remove(Step.id == step_id)
        table.insert(doc)

    return {"status": "updated", "id": step.id}


@router.delete("/steps/{step_id}", summary="Delete Step")
def delete_step(step_id: str, db: DatabaseDep):
    "Deletes a step."
    table = db.table("steps")
    Step = Query()
    
    if not table.contains(Step.id == step_id):
        raise ResourceNotFoundError(message=f"Step '{step_id}' not found.")

    table.remove(Step.id == step_id)
    return {"status": "deleted", "id": step_id}
