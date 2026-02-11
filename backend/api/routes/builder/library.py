"""Builder Library Routes.

Handles component schemas, agent toolboxes, and system configuration data.
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Header, status
from pydantic import BaseModel

from backend.dependencies import CurrentUserDep, EngineDep, RepositoryDep
from backend.models.workflow import WorkflowDefinition
from backend.services.localization import localize_schema

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---

class WorkflowTemplate(BaseModel):
    """Model representing an empty workflow template."""
    name: str
    description: str
    steps: list[str]
    default_model_mapping: dict[str, str]
    ui_schema: dict[str, Any]

# --- Registry ---

# Schema Registry for SDUI
COMPONENT_REGISTRY: dict[str, type[BaseModel]] = {
    "workflow": WorkflowDefinition,
}

# --- Endpoints ---

@router.get(
    "/schema/{component_type}",
    summary="Get Component Schema",
    response_description="JSON Schema for the requested component.",
)
async def get_component_schema(
    component_type: str,
    current_user: CurrentUserDep,
):
    """Retrieve the JSON Schema for a specific component type (SDUI)."""
    model_class = COMPONENT_REGISTRY.get(component_type)

    if not model_class:
        from backend.exceptions import ResourceNotFoundError

        error_code = "COMPONENT_SCHEMA_NOT_FOUND"
        logger.error(f"{error_code}: Type '{component_type}' not in registry.", exc_info=True)
        raise ResourceNotFoundError("ComponentSchema", component_type, details={"error_code": error_code})

    schema = model_class.model_json_schema()
    return localize_schema(schema)


@router.get(
    "/config/agents",
    summary="List Agent Class Metadata",
    response_description="A list of agent definitions including I/O contracts.",
)
async def get_available_agents(engine: EngineDep):
    """Returns metadata for all registered agents, used for the Builder Toolbox."""
    try:
        registry = engine.registry
        agents_meta = []
        agents = registry.get_all_agents()

        for name, agent_inst in agents.items():
            agent_cls = agent_inst.__class__
            meta = {
                "name": name,
                "description": agent_cls.__doc__ or "No description.",
                "inputs": getattr(agent_cls, "INPUT_REQUIREMENTS", []),
                "outputs": [],
            }
            agents_meta.append(meta)

        return agents_meta
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "AGENT_LISTING_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.get("/config/template", summary="Get Template", response_description="Empty workflow template.")
async def get_workflow_template():
    """Returns a valid empty workflow template."""
    return WorkflowTemplate(
        name="New Workflow", description="", steps=[], default_model_mapping={}, ui_schema={"nodes": []}
    )


@router.get("/config/fusion-rules", summary="Get Fusion Rules", response_description="List of fusion rules.")
async def get_fusion_rules(repository: RepositoryDep):
    """Returns validation rules for prompt fusion."""
    rules = []
    all_steps = await repository.get_all_steps()
    for s in all_steps:
        if "fusion_info" in s:
            rules.append(
                {
                    "composite_step_id": s["id"],
                    "name": s.get("name", s["id"]),
                    "replaces_components": s["fusion_info"].get("replaces_components", []),
                    "min_steps": s["fusion_info"].get("min_steps", 2),
                }
            )
    return rules


@router.get("/config/prompt-types", summary="Get Prompt Types", response_description="List of allowed types.")
async def get_prompt_types():
    """Returns list of component types that can be used as prompts."""
    return ["prompt", "mandate", "rule", "header", "instruction"]


@router.get(
    "/seed_data",
    summary="Get Seed Data",
    response_description="Returns the full components, steps, and workflows from the database.",
)
async def get_seed_data(repository: RepositoryDep, current_user: CurrentUserDep):
    """Retrieves the raw seed data configuration (components, steps, workflows).

    Now scoped by User Role (Root sees all).
    """
    try:
        # Note: repository methods are async
        components = await repository.get_all_components()
        steps = await repository.get_all_steps()

        # Pass Role/Org for filtering
        workflows = await repository.get_all_workflows(
            organization_id=current_user.organization_id, role=current_user.role
        )

        return {"components": components, "steps": steps, "workflows": workflows}
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "SEED_DATA_RETRIEVAL_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        ) from e


