"""API Router for System Configuration.

This module provides endpoints for managing configuration components (prompts, mandates),
model settings, and system-wide ontology (dimensions).
"""

import inspect
import json
import logging
import re
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path, status
from fastapi import Query as APIQuery
from pydantic import BaseModel, Field
from tinydb import Query

# --- Local Imports ---
# Rule 6: APIError must be the FIRST local import
from backend.schemas.error import APIError
from backend.database.exporter import export_db_to_files
from backend.dependencies import DatabaseDep, LLMHandlerDep, RegistryDep
from backend.models import domain as schemas
from backend.seed.seeder import seed_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["Configuration"])

# ... Models (ComponentUpdate, etc) omitted for brevity as they don't change ...
# (Kept in actual edit but abbreviated here for display)


class ComponentUpdate(BaseModel):
    """Payload for updating a configuration component.

    Attributes:
        content (str | dict | list): The template content.
        description (str): Metadata description.
        citation (str): Short citation anchor.
        citation_full (str): Complete bibliographic reference.
        type (str): Component categorization.
    """

    content: Annotated[
        str | dict[str, Any] | list[Any],
        Field(description="The template content (prompt text, rule text, or config object)."),
    ]
    description: Annotated[str | None, Field(description="Metadata description.")] = None
    citation: Annotated[str | None, Field(description="Short citation anchor.")] = None
    citation_full: Annotated[str | None, Field(description="Complete bibliographic reference.")] = None
    type: Annotated[
        str | None, Field(description="Component categorization (e.g. 'mandate', 'prompt', 'evaluation_matrix').")
    ] = None


class ModelSettings(BaseModel):
    """Configuration settings for a specific model strategy."""

    model_name: Annotated[str, Field(description="The concrete model identifier (e.g. 'gemini-1.5-pro').")]
    temperature: Annotated[float | None, Field(description="Sampling temperature.")] = None
    max_tokens: Annotated[int | None, Field(description="Maximum output token limit.")] = None
    top_p: Annotated[float | None, Field(description="Nucleus sampling parameter.")] = None


class GlobalModelConfig(BaseModel):
    """Global configuration for model strategies."""

    registry: Annotated[
        dict[str, dict[str, ModelSettings]], Field(description="Nested map: Provider -> Strategy -> Settings.")
    ]


class WorkflowUpdate(BaseModel):
    """Payload for updating a workflow."""

    steps: Annotated[list[dict[str, Any]] | None, Field(description="Complete list of step configurations.")] = None
    sequence: Annotated[list[str] | None, Field(description="Ordered list of step IDs.")] = None
    description: Annotated[str | None, Field(description="User-facing workflow description.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Map of StepID -> ModelStrategyKey.")] = (
        None
    )


class ComponentCreate(BaseModel):
    """Payload for creating a new component."""

    id: Annotated[str, Field(description="Unique Identifier for the component.")]
    name: Annotated[str, Field(description="Human readable name.")]
    type: Annotated[str, Field(description="Component Type (header, prompt, evaluation_matrix, etc).")]
    content: Annotated[str | dict[str, Any] | list[Any], Field(description="The content (text or JSON object).")]
    description: Annotated[str | None, Field(description="Description of purpose.")] = None
    citation: Annotated[str | None, Field(description="Short citation.")] = None
    citation_full: Annotated[str | None, Field(description="Full citation.")] = None
    module: Annotated[str | None, Field(description="Source module (legacy).")] = "config"
    component_class: Annotated[str | None, Field(description="Class name.")] = "ConfigComponent"


class WorkflowCreate(BaseModel):
    """Payload for creating a new workflow."""

    id: Annotated[str, Field(description="New Workflow UUID/Slug.")]
    name: Annotated[str, Field(description="Workflow Name.")]
    sequence: Annotated[list[str], Field(description="List of Step IDs.")] = []
    description: Annotated[str | None, Field(description="Description.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Step-Model map.")] = {}


class LLMCallRequest(BaseModel):
    """Payload for ad-hoc LLM calls."""

    provider: Annotated[str, Field(description="Provider key (google, openai, mock).")]
    mode: Annotated[str, Field(description="Strategy mode (fast, smart, etc).")]
    prompt: Annotated[str, Field(description="Input prompt text.")]
    system_instruction: Annotated[str | None, Field(description="Optional system context.")] = None


# --- Endpoints ---


@router.get("/components", summary="List Components", response_description="All configuration components.")
def get_components(db: DatabaseDep):
    """Retrieves all defined configuration components (Prompts, Mandates, Rules, etc).

    Args:
        db (DatabaseDep): Database dependency.

    Returns:
        list[dict]: List of configuration components.
    """
    return db.table("components").all()


@router.get("/components/{comp_id}", summary="Get Component", response_description="The requested component.")
def get_component(db: DatabaseDep, comp_id: str = Path(..., description="Component ID or Name")):
    """Retrieves a single component by ID or Name."""
    Component = Query()
    res = db.table("components").search(Component.id == comp_id)
    if not res:
        res = db.table("components").search(Component.name == comp_id)

    if not res:
        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)
    return res[0]


@router.post("/components", summary="Create Component", response_description="Status and ID.")
def create_component(comp: ComponentCreate, db: DatabaseDep):
    """Creates a new configuration component."""
    table = db.table("components")
    if table.search(Query().id == comp.id):
        error_code = "COMPONENT_ID_EXISTS"
        logger.error(f"{error_code}: ID {comp.id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)

    new_comp = comp.model_dump()
    if "component_class" in new_comp:
        new_comp["class"] = new_comp.pop("component_class")

    table.insert(new_comp)
    return {"status": "created", "id": comp.id}


@router.put("/components/{comp_id}", summary="Update Component", response_description="Update status.")
def update_component(comp_id: str, update: ComponentUpdate, db: DatabaseDep):
    """Updates an existing component's content and metadata.

    Args:
        comp_id (str): The ID of the component to update.
        update (ComponentUpdate): The new data.
        db (DatabaseDep): Database dependency.

    Returns:
        dict: Status and ID.

    Raises:
        HTTPException: If not found (404).
    """
    Component = Query()
    table = db.table("components")

    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)

    update_data = {"content": update.content}
    if update.description:
        update_data["description"] = update.description
    if update.citation:
        update_data["citation"] = update.citation
    if update.citation_full:
        update_data["citation_full"] = update.citation_full
    if update.type:
        update_data["type"] = update.type

    table.update(update_data, (Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "updated", "id": comp_id}


@router.delete("/components/{comp_id}", summary="Delete Component", response_description="Delete status.")
def delete_component(comp_id: str, db: DatabaseDep):
    """Deletes a component if it is not referenced by any existing steps."""
    table = db.table("components")
    Component = Query()

    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)

    # Referential Integrity Check
    steps = db.table("steps").all()
    used_in = []
    for s in steps:
        if s.get("component") == comp_id:
            used_in.append(s["id"])
            continue
        prompts = s.get("execution_config", {}).get("llm_prompts", [])
        if comp_id in prompts:
            used_in.append(s["id"])

    if used_in:
        error_code = "COMPONENT_IN_USE"
        logger.error(f"{error_code}: ID {comp_id} used in {used_in}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_code)

    table.remove((Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "deleted", "id": comp_id}


@router.get("/steps", summary="List Steps", response_description="All steps.")
def get_steps(db: DatabaseDep):
    """List all steps."""
    return db.table("steps").all()


@router.post("/steps", summary="Create Step", response_description="Created ID.")
def create_step(step: dict[str, Any], db: DatabaseDep):
    """Create a new step configuration."""
    table = db.table("steps")
    if table.search(Query().id == step.get("id")):
        error_code = "STEP_ID_EXISTS"
        logger.error(f"{error_code}: ID {step.get('id')}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)
    table.insert(step)
    return {"status": "created", "id": step.get("id")}


@router.put("/steps/{step_id}", summary="Update Step", response_description="Update status.")
def update_step(step_id: str, step: dict[str, Any], db: DatabaseDep):
    """Update a step configuration."""
    table = db.table("steps")
    if not table.search(Query().id == step_id):
        error_code = "STEP_NOT_FOUND"
        logger.error(f"{error_code}: ID {step_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)
    table.update(step, Query().id == step_id)
    return {"status": "updated", "id": step_id}


@router.delete("/steps/{step_id}", summary="Delete Step", response_description="Delete status.")
async def delete_step(step_id: str, db: DatabaseDep):
    """Delete a step.

    Refactored to enforce Integrity: Cannot delete step if used in Workflows.
    """
    # 1. Check Existence
    table = db.table("steps")
    if not table.search(Query().id == step_id):
        error_code = "STEP_NOT_FOUND"
        logger.error(f"{error_code}: ID {step_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)

    # 2. Integrity Check: Workflow Usage
    workflows = db.table("workflows").all()
    used_in = []
    for wf in workflows:
        if step_id in wf.get("steps", []) or step_id in wf.get("sequence", []):
            used_in.append(wf.get("name", wf["id"]))

    if used_in:
        error_code = "STEP_IN_USE"
        logger.error(f"{error_code}: ID {step_id} used in {used_in}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_code)

    # 3. Delete
    table.remove(Query().id == step_id)
    return {"status": "deleted", "id": step_id}


@router.get("/workflows", summary="List Workflows", response_description="All workflows.")
def get_workflows(db: DatabaseDep):
    """List all workflows."""
    return db.table("workflows").all()


@router.get("/workflows/{wf_id}", summary="Get Workflow", response_description="Requested workflow.")
def get_workflow(wf_id: str, db: DatabaseDep):
    """Get a specific workflow."""
    Workflow = Query()
    res = db.table("workflows").search(Workflow.id == wf_id)
    if not res:
        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)
    return res[0]


@router.put("/workflows/{wf_id}", summary="Update Workflow", response_description="Update status.")
def update_workflow(wf_id: str, update: WorkflowUpdate, db: DatabaseDep):
    """Update a workflow definition."""
    Workflow = Query()
    table = db.table("workflows")

    if not table.search(Workflow.id == wf_id):
        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)

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
        error_code = "NO_UPDATE_DATA"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)

    steps_to_check = update.steps if update.steps else update.sequence
    if steps_to_check:
        valid_steps = {s["id"] for s in db.table("steps").all()}
        for item in steps_to_check:
            sid = item if isinstance(item, str) else item.get("id")
            if sid and sid not in valid_steps:
                error_code = "INVALID_STEP_ID"
                logger.error(f"{error_code}: Step {sid} not found.", exc_info=True)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)

    table.update(update_data, Workflow.id == wf_id)
    return {"status": "updated", "id": wf_id}


@router.post("/workflows", summary="Create Workflow", response_description="Created ID.")
def create_workflow(workflow: WorkflowCreate, db: DatabaseDep):
    """Create a new workflow."""
    Workflow = Query()
    table = db.table("workflows")

    if table.search(Workflow.id == workflow.id):
        error_code = "WORKFLOW_ID_EXISTS"
        logger.error(f"{error_code}: ID {workflow.id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)

    new_wf = workflow.model_dump()
    if workflow.sequence:
        valid_steps = {s["id"] for s in db.table("steps").all()}
        for step_id in workflow.sequence:
            if step_id not in valid_steps:
                error_code = "INVALID_STEP_ID"
                logger.error(f"{error_code}: Step {step_id} not found.", exc_info=True)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)

    table.insert(new_wf)
    return {"status": "created", "id": workflow.id}


@router.delete("/workflows/{wf_id}", summary="Delete Workflow", response_description="Delete status.")
def delete_workflow(wf_id: str, db: DatabaseDep):
    """Delete a workflow."""
    Workflow = Query()
    table = db.table("workflows")
    if not table.search(Workflow.id == wf_id):
        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {wf_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_code)
    table.remove(Workflow.id == wf_id)
    return {"status": "deleted", "id": wf_id}


@router.post("/export-seed", summary="Export DB to Files", response_description="Export status.")
def export_seed_data(background_tasks: BackgroundTasks):
    """Trigger background export."""
    background_tasks.add_task(export_db_to_files)
    return {"status": "export_started", "message": "Exporting DB to files in background."}


@router.post("/reset-from-seed", summary="Reset DB from Seed", response_description="Reset status.")
def reset_from_seed():
    """Wipe DB and reload from seed_data.json."""
    try:
        seed_database()
        return {"status": "success", "message": "Database reset from seed data."}
    except Exception as e:
        error_code = "DB_RESET_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_code) from e


@router.post("/deploy-mock-to-prod", summary="Deploy Mock -> Prod", response_description="Deployment status.")
def deploy_mock_to_prod():
    """Migrate Mock DB state to Production DB (destructive)."""
    from backend.settings import get_settings

    settings = get_settings()
    try:
        export_db_to_files(source_db_path=settings.mock_db_path)
        seed_database(target_db_path=settings.prod_db_path)
        return {"status": "success", "message": "Mock environment deployed to Production DB."}
    except Exception as e:
        error_code = "DB_DEPLOY_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_code) from e


@router.post("/deploy-prod-to-mock", summary="Deploy Prod -> Mock", response_description="Deployment status.")
def deploy_prod_to_mock():
    """Overwrite Mock DB with Production DB state."""
    from backend.settings import get_settings

    settings = get_settings()
    try:
        export_db_to_files(source_db_path=settings.prod_db_path)
        seed_database(target_db_path=settings.mock_db_path)
        return {"status": "success", "message": "Production environment deployed to Mock DB."}
    except Exception as e:
        error_code = "DB_DEPLOY_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_code) from e


@router.get("/schemas", summary="List Schemas", response_description="All Pydantic Schemas.")
def get_schemas():
    """Get all available JSON Schemas."""
    schema_data = {}
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            try:
                json_schema = obj.model_json_schema()
                example = None
                if hasattr(obj, "model_config"):
                    config: dict[str, Any] = dict(obj.model_config)
                    if "json_schema_extra" in config:
                        extra = config["json_schema_extra"]
                        if isinstance(extra, dict) and "examples" in extra and extra["examples"]:
                            example = extra["examples"][0]
                schema_data[name] = {"schema": json_schema, "example": example}
            except Exception as e:
                logger.error(f"Error processing schema {name}: {e}")
    return schema_data


@router.get("/unified-prompts", summary="Get Unified Prompts", response_description="Full Markdown text.")
def get_unified_prompts(db: DatabaseDep):
    """Generate the Unified Master View."""
    try:
        schema_data = _fetch_schemas()
        all_components = db.table("components").all()
        unified_text = _build_unified_view(all_components, schema_data)
        return {"content": unified_text}
    except Exception as e:
        error_code = "UNIFIED_PROMPT_GENERATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_code) from e


# Helpers (kept same)
def _fetch_schemas() -> dict[str, Any]:
    schema_data = {}
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            try:
                json_schema = obj.model_json_schema()
                example = None
                if hasattr(obj, "model_config"):
                    config: dict[str, Any] = dict(obj.model_config)
                    if "json_schema_extra" in config:
                        extra = config["json_schema_extra"]
                        if isinstance(extra, dict) and "examples" in extra and extra["examples"]:
                            example = extra["examples"][0]
                schema_data[name] = {"schema": json_schema, "example": example}
            except Exception:
                pass
    return schema_data


def _expand_content(text: Any, schemas: dict[str, Any]) -> str:
    if not text:
        return ""
    if isinstance(text, list):
        text = "\n".join(str(x) for x in text)
    if not isinstance(text, str):
        text = str(text)

    def replace_match(match):
        schema_name = match.group(1)
        is_example = match.group(2) is not None
        if schema_name in schemas:
            data = schemas[schema_name]
            if is_example and data.get("example"):
                return f"```json\n{json.dumps(data['example'], indent=2, ensure_ascii=False)}\n```"
            elif not is_example and data.get("schema"):
                return f"```json\n{json.dumps(data['schema'], indent=2, ensure_ascii=False)}\n```"
        return match.group(0)

    pattern = r"\[Ks\. schemas\.py / ([a-zA-Z0-9_]+)( / EXAMPLE)?\]"
    return re.sub(pattern, replace_match, text)


def _build_unified_view(components: list, schema_data: dict[str, Any]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for c in components:
        ctype = c.get("type", "other")
        if ctype not in grouped:
            grouped[ctype] = []
        grouped[ctype].append(c)
    type_order = ["header", "mandate", "rule", "principle", "protocol", "method", "heuristic", "requirement", "prompt"]
    unified_text = "# KOGNITIIVINEN KVOORUM - SYSTEM PROMPTS & SCHEMAS\n\n"

    def process_comp_list(comps):
        text = ""
        sorted_comps = sorted(comps, key=lambda x: str(x.get("id") or ""))
        for comp in sorted_comps:
            text += f"### {comp.get('id')} ({comp.get('type')})\n\n"
            text += f"{_expand_content(comp.get('content', ''), schema_data)}\n\n---\n\n"
        return text

    for ctype in type_order:
        if ctype in grouped:
            unified_text += process_comp_list(grouped[ctype])
    for ctype, comps in grouped.items():
        if ctype not in type_order:
            unified_text += process_comp_list(comps)
    return unified_text


@router.get(
    "/models/available",
    summary="List Available Models",
    response_description="Dictionary of verified available models from Providers.",
)
def list_available_models(
    handler: LLMHandlerDep,
    providers: Annotated[list[str] | None, APIQuery(description="List of providers (google, openai, mock)")] = None,
    location: Annotated[str | None, APIQuery(description="Region for Google Cloud (defaults to env config)")] = None,
):
    """Returns a dynamic dictionary of models found via provider APIs.

    Supports filtering by provider and specifying Google Cloud region.

    Args:
        handler (LLMHandlerDep): LLM Handler dependency.
        providers (list[str]): Optional list of providers to query.
        location (str): Optional region override.

    Returns:
        dict: Map of provider -> list of models.
    """
    # Map 'moc' to 'mock' if user sends it (as requested)
    if providers:
        providers = [p if p != "moc" else "mock" for p in providers]

    return handler.fetch_all_available_models(providers=providers, location=location)


@router.get("/models/registry", summary="Get Model Registry", response_description="Registry Dict.")
def get_model_registry(handler: LLMHandlerDep):
    """Get global model registry via Handler."""
    return handler.get_active_model_registry()


@router.post("/models/registry", summary="Update Registry", response_description="Updated registry.")
def update_model_registry(config: GlobalModelConfig, db: DatabaseDep):
    """Update global model registry.

    Args:
        config (GlobalModelConfig): The new registry configuration.
        db (DatabaseDep): Database dependency.

    Returns:
        dict: Status and updated registry.
    """
    table = db.table("system_config")
    Config = Query()
    # Serialize safe
    raw_json = config.model_dump_json() if hasattr(config, "model_dump_json") else config.json()
    registry_data = json.loads(raw_json)["registry"]
    table.upsert({"type": "model_registry", "models": registry_data}, Config.type == "model_registry")
    return {"status": "updated", "registry": registry_data}


@router.post("/models/call", summary="Call LLM (Ad-hoc)", response_description="Generated text response.")
async def call_llm_adhoc(request: LLMCallRequest, handler: LLMHandlerDep):
    """Execute a direct LLM call using the Handler's logic (resolving config from registry).

    Args:
        request (LLMCallRequest): The prompt and settings.
        handler (LLMHandlerDep): LLM Handler dependency.

    Returns:
        dict: The content string from the LLM.

    Raises:
        HTTPException: If call fails (500).
    """
    try:
        response_text = await handler.call_llm(
            provider=request.provider,
            mode=request.mode,
            prompt=request.prompt,
            system_instruction=request.system_instruction,
        )
        return {"content": response_text}
    except Exception as e:
        error_code = "AD_HOC_LLM_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_code) from e


@router.get("/models/strategies", summary="Get Strategies", response_description="Active strategy map.")
def get_model_strategies(db: DatabaseDep):
    """Get active model strategies."""
    logger.info("Fetching model strategies...")
    try:
        table = db.table("system_config")
        Config = Query()
        res = table.search(Config.type == "model_registry")
        if res and "models" in res[0]:
            registry = res[0]["models"]
            if "google" in registry and registry["google"]:
                return registry["google"]
            if "openai" in registry and registry["openai"]:
                return registry["openai"]
    except Exception as e:
        logger.error(f"Error fetching strategies: {e}")
    from backend.settings import get_settings

    return get_settings().model_strategies


@router.get("/introspection", summary="Introspect Agents", response_description="Discovery report.")
def get_introspection():
    """Discover agents and schemas."""
    # (Implementation details omitted for brevity as they use no DB or LLM deps)
    available_schemas = []
    # ... (rest of implementation)

    # Needs to be same as before
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            available_schemas.append(name)
    import importlib
    import pkgutil

    import backend.agents
    from backend.agents.base import BaseAgent

    available_agents = []
    available_hooks = set()
    package = backend.agents
    prefix = package.__name__ + "."
    for _, name, _ispkg in pkgutil.iter_modules(package.__path__, prefix):
        if name == "backend.agents.base":
            continue
        try:
            module = importlib.import_module(name)
            for cls_name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    available_agents.append(cls_name)
                    base_methods = set(dir(BaseAgent))
                    for method_name, method in inspect.getmembers(obj):
                        if (inspect.isfunction(method) or inspect.ismethod(method)) and not method_name.startswith("_"):
                            if method_name not in base_methods and method_name not in [
                                "get_response_schema",
                                "execute",
                            ]:
                                available_hooks.add(f"{cls_name}.{method_name}")
        except Exception:
            continue
    return {
        "schemas": sorted(available_schemas),
        "agents": sorted(available_agents),
        "hooks": sorted(list(available_hooks)),
    }


# Duplicate endpoint removed. Use list_available_models above.


class DimensionDefinition(BaseModel):
    """Model definition for an evaluation dimension."""

    id: Annotated[str, Field(description="Unique dimension ID (e.g. 'analyysi').")]
    label: Annotated[str, Field(description="Human readable default label.")]
    description: Annotated[str | None, Field(description="Explanation of what this measures.")] = None
    is_system: Annotated[bool, Field(description="If true, is a core system dimension.")] = False


@router.get(
    "/ontology/dimensions",
    summary="Get Known Dimensions",
    response_description="List of unique evaluation dimension IDs.",
)
def get_known_dimensions(db: DatabaseDep):
    """Returns specific allowed dimension IDs from the ontology table.

    Auto-seeds defaults if table is empty.

    Args:
        db (DatabaseDep): Database dependency.

    Returns:
        list[str]: Sorted list of dimension IDs.
    """
    table = db.table("dimensions")
    all_dims = table.all()

    if not all_dims:
        # Seeding defaults
        defaults = [
            {
                "id": "analyysi",
                "label": "Analyysi",
                "description": "Ymmärryksen syvyys ja ongelman rajaus.",
                "is_system": True,
            },
            {
                "id": "arviointi",
                "label": "Arviointi",
                "description": "Ratkaisun validointi ja perustelu.",
                "is_system": True,
            },
            {"id": "synteesi", "label": "Synteesi", "description": "Uuden luominen ja yhdistely", "is_system": True},
            {"id": "agency", "label": "Agency", "description": "Toimijuus ja prosessin hallinta.", "is_system": True},
            {
                "id": "engineering",
                "label": "Engineering",
                "description": "Tekninen toteutus ja promptaus.",
                "is_system": True,
            },
            {
                "id": "falsification",
                "label": "Falsification",
                "description": "Kriittinen iteraatio ja virheiden etsintä.",
                "is_system": True,
            },
        ]
        for d in defaults:
            table.insert(d)
        all_dims = defaults

    return sorted([d["id"] for d in all_dims])


@router.get("/ontology/dimensions/full", summary="Get Full Ontology", response_description="Full dimension objects.")
def get_full_ontology(db: DatabaseDep):
    """Retrieve all dimension objects from the ontology."""
    get_known_dimensions(db)  # Ensure seed
    return db.table("dimensions").all()


@router.post("/ontology/dimensions", summary="Create Dimension", response_description="Created Dimension.")
def create_dimension(dim: DimensionDefinition, db: DatabaseDep):
    """Create a new evaluation dimension."""
    table = db.table("dimensions")
    if table.search(Query().id == dim.id):
        error_code = "DIMENSION_EXISTS"
        logger.error(f"{error_code}: ID {dim.id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_code)
    table.insert(dim.model_dump())
    return {"status": "created", "id": dim.id}


@router.delete("/ontology/dimensions/{dim_id}", summary="Delete Dimension", response_description="Status.")
def delete_dimension(dim_id: str, db: DatabaseDep):
    """Delete a dimension if not in use."""
    # 1. Check Usage
    comp_table = db.table("components")
    Component = Query()
    matrices = comp_table.search(Component.type == "evaluation_matrix")

    used_in = []
    for m in matrices:
        content = m.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                continue
        criteria = content.get("criteria", [])
        for c in criteria:
            if c.get("id") == dim_id:
                used_in.append(m.get("name", m["id"]))
                break

    if used_in:
        error_code = "DIMENSION_IN_USE"
        logger.error(f"{error_code}: ID {dim_id} used in {used_in}", exc_info=True)
        raise HTTPException(
            status_code=409,
            detail=error_code,
        )

    # 2. Delete
    table = db.table("dimensions")
    table.remove(Query().id == dim_id)
    return {"status": "deleted", "id": dim_id}


@router.post("/validate-flow", summary="Validate Flow", response_description="Validation Report.")
async def validate_flow(workflow: WorkflowCreate, db: DatabaseDep, registry: RegistryDep):
    """Dry run validation."""
    from backend.core.factory import AgentFactory

    # Strict Resolution: Use 'fast' strategy for validation dry-run
    try:
        config = await registry.resolve_model_config("fast")
        agents_map = AgentFactory.create_agents_map(initial_model=config["model_name"])
    except Exception as e:
        error_code = "FACTORY_ERROR"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_code) from e

    known_keys = ["history_text", "product_text", "reflection_text", "bibliography_context"]
    errors = []
    trace_log: list[str] = []
    all_steps_config = db.table("steps").all()
    steps_db_map = {s["id"]: s for s in all_steps_config}
    pseudo_state = list(known_keys)

    for i, step_id in enumerate(workflow.sequence):
        if step_id not in steps_db_map:
            errors.append(f"Unknown Step: {step_id}")
            continue
        step_doc = steps_db_map[step_id]
        agent_name = step_doc.get("component")
        if not agent_name or agent_name not in agents_map:
            errors.append(f"Unknown Agent: {agent_name} in {step_id}")
            continue
        agent_instance = agents_map[agent_name]
        reqs = getattr(agent_instance, "REQUIRES_KEYS", [])
        missing = [r for r in reqs if r not in pseudo_state]
        if missing:
            errors.append(f"Step {i + 1} Missing: {missing}")
        prods = getattr(agent_instance, "PRODUCES_KEYS", [])
        for k in prods:
            if k not in pseudo_state:
                pseudo_state.append(k)

    return {"valid": len(errors) == 0, "errors": errors, "trace": trace_log, "final_state_keys": pseudo_state}
