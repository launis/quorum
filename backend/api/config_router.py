from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Path, Query as APIQuery
from tinydb import Query
from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
import json
import re
import inspect
import logging

from backend.database.exporter import export_db_to_files
from backend.database.seeder import seed_database
from backend.database.wrapper import AbstractDatabase
from backend.dependencies import get_db_client_dep
from backend.models import domain as schemas

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

# --- Models ---

class ComponentUpdate(BaseModel):
    content: Annotated[str, Field(description="The template content (prompt text, rule text).")]
    description: Annotated[Optional[str], Field(description="Metadata description.")] = None
    citation: Annotated[Optional[str], Field(description="Short citation anchor.")] = None
    citation_full: Annotated[Optional[str], Field(description="Complete bibliographic reference.")] = None
    type: Annotated[Optional[str], Field(description="Component categorization (e.g. 'mandate', 'prompt').")] = None

class ModelSettings(BaseModel):
    model_name: Annotated[str, Field(description="The concrete model identifier (e.g. 'gemini-1.5-pro').")]
    temperature: Annotated[Optional[float], Field(description="Sampling temperature.")] = None
    max_tokens: Annotated[Optional[int], Field(description="Maximum output token limit.")] = None
    top_p: Annotated[Optional[float], Field(description="Nucleus sampling parameter.")] = None

class GlobalModelConfig(BaseModel):
    registry: Annotated[Dict[str, Dict[str, ModelSettings]], Field(
        description="Nested map: Provider -> Strategy -> Settings."
    )]

class WorkflowUpdate(BaseModel):
    steps: Annotated[Optional[List[Dict[str, Any]]], Field(description="Complete list of step configurations.")] = None
    sequence: Annotated[Optional[List[str]], Field(description="Ordered list of step IDs.")] = None
    description: Annotated[Optional[str], Field(description="User-facing workflow description.")] = None
    default_model_mapping: Annotated[Optional[Dict[str, str]], Field(description="Map of StepID -> ModelStrategyKey.")] = None

class ComponentCreate(BaseModel):
    id: Annotated[str, Field(description="Unique Identifier for the component.")]
    name: Annotated[str, Field(description="Human readable name.")]
    type: Annotated[str, Field(description="Component Type (header, prompt, etc).")]
    content: Annotated[str, Field(description="The raw text content.")]
    description: Annotated[Optional[str], Field(description="Description of purpose.")] = None
    citation: Annotated[Optional[str], Field(description="Short citation.")] = None
    citation_full: Annotated[Optional[str], Field(description="Full citation.")] = None
    module: Annotated[Optional[str], Field(description="Source module (legacy).")] = "config"
    component_class: Annotated[Optional[str], Field(description="Class name.")] = "ConfigComponent"

class WorkflowCreate(BaseModel):
    id: Annotated[str, Field(description="New Workflow UUID/Slug.")]
    name: Annotated[str, Field(description="Workflow Name.")]
    sequence: Annotated[List[str], Field(description="List of Step IDs.")] = []
    description: Annotated[Optional[str], Field(description="Description.")] = None
    default_model_mapping: Annotated[Optional[Dict[str, str]], Field(description="Step-Model map.")] = {}


# --- Endpoints ---

@router.get(
    "/components", 
    summary="List Components",
    response_description="All configuration components."
)
def get_components(db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Retrieves all defined configuration components (Prompts, Mandates, Rules, etc).
    """
    return db.table('components').all()

@router.get(
    "/components/{comp_id}", 
    summary="Get Component",
    response_description="The requested component."
)
def get_component(
    comp_id: str = Path(..., description="Component ID or Name"), 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Retrieves a single component by ID or Name.
    """
    Component = Query()
    res = db.table('components').search(Component.id == comp_id)
    if not res:
        res = db.table('components').search(Component.name == comp_id)
    
    if not res:
        raise HTTPException(status_code=404, detail="Component not found")
    return res[0]

@router.post(
    "/components", 
    summary="Create Component",
    response_description="Status and ID."
)
def create_component(
    comp: ComponentCreate, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Creates a new configuration component.
    """
    table = db.table('components')
    if table.search(Query().id == comp.id):
        raise HTTPException(status_code=400, detail="Component ID already exists")
    
    new_comp = comp.model_dump()
    if 'component_class' in new_comp:
        new_comp['class'] = new_comp.pop('component_class')
        
    table.insert(new_comp)
    return {"status": "created", "id": comp.id}

@router.put(
    "/components/{comp_id}", 
    summary="Update Component",
    response_description="Update status."
)
def update_component(
    comp_id: str, 
    update: ComponentUpdate, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Updates an existing component's content and metadata.
    """
    Component = Query()
    table = db.table('components')
    
    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        raise HTTPException(status_code=404, detail="Component not found")
    
    update_data = {"content": update.content}
    if update.description: update_data["description"] = update.description
    if update.citation: update_data["citation"] = update.citation
    if update.citation_full: update_data["citation_full"] = update.citation_full
    if update.type: update_data["type"] = update.type
        
    table.update(update_data, (Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "updated", "id": comp_id}

@router.delete(
    "/components/{comp_id}", 
    summary="Delete Component",
    response_description="Delete status."
)
def delete_component(
    comp_id: str, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Deletes a component if it is not referenced by any existing steps.
    """
    table = db.table('components')
    Component = Query()
    
    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Referential Integrity Check
    steps = db.table('steps').all()
    used_in = []
    for s in steps:
        if s.get('component') == comp_id:
            used_in.append(s['id'])
            continue
        prompts = s.get('execution_config', {}).get('llm_prompts', [])
        if comp_id in prompts:
            used_in.append(s['id'])
            
    if used_in:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete component '{comp_id}'. Used in steps: {', '.join(used_in[:3])}..."
        )
        
    table.remove((Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "deleted", "id": comp_id}

@router.get(
    "/steps", 
    summary="List Steps",
    response_description="All steps."
)
def get_steps(db: AbstractDatabase = Depends(get_db_client_dep)):
    """List all steps."""
    return db.table('steps').all()

@router.post(
    "/steps", 
    summary="Create Step",
    response_description="Created ID."
)
def create_step(
    step: Dict[str, Any], 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """Create a new step configuration."""
    table = db.table('steps')
    if table.search(Query().id == step.get('id')):
        raise HTTPException(status_code=400, detail="Step ID already exists")
    table.insert(step)
    return {"status": "created", "id": step.get('id')}

@router.put(
    "/steps/{step_id}", 
    summary="Update Step",
    response_description="Update status."
)
def update_step(
    step_id: str, 
    step: Dict[str, Any], 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """Update a step configuration."""
    table = db.table('steps')
    if not table.search(Query().id == step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    table.update(step, Query().id == step_id)
    return {"status": "updated", "id": step_id}

@router.delete(
    "/steps/{step_id}", 
    summary="Delete Step",
    response_description="Delete status."
)
def delete_step(
    step_id: str, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """Delete a step."""
    table = db.table('steps')
    if not table.search(Query().id == step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    table.remove(Query().id == step_id)
    return {"status": "deleted", "id": step_id}

@router.get(
    "/workflows", 
    summary="List Workflows",
    response_description="All workflows."
)
def get_workflows(db: AbstractDatabase = Depends(get_db_client_dep)):
    """List all workflows."""
    return db.table('workflows').all()

@router.get(
    "/workflows/{wf_id}", 
    summary="Get Workflow",
    response_description="Requested workflow."
)
def get_workflow(
    wf_id: str, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """Get a specific workflow."""
    Workflow = Query()
    res = db.table('workflows').search(Workflow.id == wf_id)
    if not res:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return res[0]

@router.put(
    "/workflows/{wf_id}", 
    summary="Update Workflow",
    response_description="Update status."
)
def update_workflow(
    wf_id: str, 
    update: WorkflowUpdate, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """Update a workflow definition."""
    Workflow = Query()
    table = db.table('workflows')
    
    if not table.search(Workflow.id == wf_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    update_data = {}
    if update.steps is not None: update_data["steps"] = update.steps
    if update.sequence is not None: update_data["sequence"] = update.sequence
    if update.description: update_data["description"] = update.description
    if update.default_model_mapping is not None: update_data["default_model_mapping"] = update.default_model_mapping
        
    if not update_data:
         raise HTTPException(status_code=400, detail="No data to update")

    steps_to_check = update.steps if update.steps else update.sequence
    if steps_to_check:
        valid_steps = {s['id'] for s in db.table('steps').all()}
        for item in steps_to_check:
            sid = item if isinstance(item, str) else item.get('id')
            if sid and sid not in valid_steps:
                 raise HTTPException(status_code=400, detail=f"Invalid Step ID: '{sid}' does not exist.")

    table.update(update_data, Workflow.id == wf_id)
    return {"status": "updated", "id": wf_id}

@router.post(
    "/workflows", 
    summary="Create Workflow",
    response_description="Created ID."
)
def create_workflow(
    workflow: WorkflowCreate, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """Create a new workflow."""
    Workflow = Query()
    table = db.table('workflows')
    
    if table.search(Workflow.id == workflow.id):
        raise HTTPException(status_code=400, detail="Workflow ID already exists")
        
    new_wf = workflow.model_dump()
    if workflow.sequence:
        valid_steps = {s['id'] for s in db.table('steps').all()}
        for step_id in workflow.sequence:
            if step_id not in valid_steps:
                 raise HTTPException(status_code=400, detail=f"Invalid Step ID: '{step_id}' does not exist.")

    table.insert(new_wf)
    return {"status": "created", "id": workflow.id}

@router.delete(
    "/workflows/{wf_id}", 
    summary="Delete Workflow",
    response_description="Delete status."
)
def delete_workflow(
    wf_id: str, 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """Delete a workflow."""
    Workflow = Query()
    table = db.table('workflows')
    if not table.search(Workflow.id == wf_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    table.remove(Workflow.id == wf_id)
    return {"status": "deleted", "id": wf_id}

@router.post(
    "/export-seed", 
    summary="Export DB to Files",
    response_description="Export status."
)
def export_seed_data(background_tasks: BackgroundTasks):
    """Trigger background export."""
    background_tasks.add_task(export_db_to_files)
    return {"status": "export_started", "message": "Exporting DB to files in background."}

@router.post(
    "/reset-from-seed", 
    summary="Reset DB from Seed",
    response_description="Reset status."
)
def reset_from_seed():
    """Wipe DB and reload from seed_data.json."""
    try:
        seed_database()
        return {"status": "success", "message": "Database reset from seed data."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/deploy-mock-to-prod", 
    summary="Deploy Mock -> Prod",
    response_description="Deployment status."
)
def deploy_mock_to_prod():
    """Migrate Mock DB state to Production DB (destructive)."""
    from backend.settings import get_settings
    settings = get_settings()
    try:
        export_db_to_files(source_db_path=settings.mock_db_path)
        seed_database(target_db_path=settings.prod_db_path)
        return {"status": "success", "message": "Mock environment deployed to Production DB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/deploy-prod-to-mock", 
    summary="Deploy Prod -> Mock",
    response_description="Deployment status."
)
def deploy_prod_to_mock():
    """Overwrite Mock DB with Production DB state."""
    from backend.settings import get_settings
    settings = get_settings()
    try:
        export_db_to_files(source_db_path=settings.prod_db_path)
        seed_database(target_db_path=settings.mock_db_path)
        return {"status": "success", "message": "Production environment deployed to Mock DB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/schemas", 
    summary="List Schemas",
    response_description="All Pydantic Schemas."
)
def get_schemas():
    """Get all available JSON Schemas."""
    schema_data = {}
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            try:
                json_schema = obj.model_json_schema()
                example = None
                if hasattr(obj, 'model_config'):
                    config = obj.model_config
                    if 'json_schema_extra' in config:
                        extra = config['json_schema_extra']
                        if 'examples' in extra and extra['examples']:
                            example = extra['examples'][0]
                schema_data[name] = {"schema": json_schema, "example": example}
            except Exception as e:
                logger.error(f"Error processing schema {name}: {e}")
    return schema_data

@router.get(
    "/unified-prompts", 
    summary="Get Unified Prompts",
    response_description="Full Markdown text."
)
def get_unified_prompts(db: AbstractDatabase = Depends(get_db_client_dep)):
    """Generate the Unified Master View."""
    try:
        schema_data = _fetch_schemas()
        all_components = db.table('components').all()
        unified_text = _build_unified_view(all_components, schema_data)
        return {"content": unified_text}
    except Exception as e:
        logger.error(f"Error generating unified prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helpers (kept same)
def _fetch_schemas() -> Dict[str, Any]:
    schema_data = {}
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            try:
                json_schema = obj.model_json_schema()
                example = None
                if hasattr(obj, 'model_config'):
                    config = obj.model_config
                    if 'json_schema_extra' in config:
                        extra = config['json_schema_extra']
                        if 'examples' in extra and extra['examples']:
                             example = extra['examples'][0]
                schema_data[name] = {"schema": json_schema, "example": example}
            except Exception: pass
    return schema_data

def _expand_content(text: Any, schemas: Dict[str, Any]) -> str:
    if not text: return ""
    if isinstance(text, list): text = "\n".join(str(x) for x in text)
    if not isinstance(text, str): text = str(text)
    
    def replace_match(match):
        schema_name = match.group(1)
        is_example = match.group(2) is not None
        if schema_name in schemas:
            data = schemas[schema_name]
            if is_example and data.get('example'):
                return f"```json\n{json.dumps(data['example'], indent=2, ensure_ascii=False)}\n```"
            elif not is_example and data.get('schema'):
                 return f"```json\n{json.dumps(data['schema'], indent=2, ensure_ascii=False)}\n```"
        return match.group(0)

    pattern = r"\[Ks\. schemas\.py / ([a-zA-Z0-9_]+)( / EXAMPLE)?\]"
    return re.sub(pattern, replace_match, text)

def _build_unified_view(components: list, schema_data: Dict[str, Any]) -> str:
    grouped = {}
    for c in components:
        ctype = c.get('type', 'other')
        if ctype not in grouped: grouped[ctype] = []
        grouped[ctype].append(c)
    type_order = ["header", "mandate", "rule", "principle", "protocol", "method", "heuristic", "requirement", "prompt"]
    unified_text = "# KOGNITIIVINEN KVOORUM - SYSTEM PROMPTS & SCHEMAS\n\n"
    def process_comp_list(comps):
        text = ""
        sorted_comps = sorted(comps, key=lambda x: str(x.get('id') or ''))
        for comp in sorted_comps:
            text += f"### {comp.get('id')} ({comp.get('type')})\n\n"
            text += f"{_expand_content(comp.get('content', ''), schema_data)}\n\n---\n\n"
        return text
    for ctype in type_order:
        if ctype in grouped: unified_text += process_comp_list(grouped[ctype])
    for ctype, comps in grouped.items():
        if ctype not in type_order: unified_text += process_comp_list(comps)
    return unified_text

@router.get(
    "/models/registry", 
    summary="Get Model Registry",
    response_description="Registry Dict."
)
def get_model_registry(db: AbstractDatabase = Depends(get_db_client_dep)):
    """Get global model registry."""
    table = db.table('system_config')
    Config = Query()
    res = table.search(Config.type == 'model_registry')
    if res: return res[0].get('models', {})
    return {}

@router.post(
    "/models/registry", 
    summary="Update Registry",
    response_description="Updated registry."
)
def update_model_registry(config: GlobalModelConfig, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Update global model registry."""
    table = db.table('system_config')
    Config = Query()
    # Serialize safe
    raw_json = config.model_dump_json() if hasattr(config, 'model_dump_json') else config.json()
    registry_data = json.loads(raw_json)['registry']
    table.upsert({'type': 'model_registry', 'models': registry_data}, Config.type == 'model_registry')
    return {"status": "updated", "registry": registry_data}

@router.get(
    "/models/strategies", 
    summary="Get Strategies",
    response_description="Active strategy map."
)
def get_model_strategies(db: AbstractDatabase = Depends(get_db_client_dep)):
    """Get active model strategies."""
    logger.info("Fetching model strategies...")
    try:
        table = db.table('system_config')
        Config = Query()
        res = table.search(Config.type == 'model_registry')
        if res and 'models' in res[0]:
            registry = res[0]['models']
            if 'google' in registry and registry['google']: return registry['google']
            if 'openai' in registry and registry['openai']: return registry['openai']
    except Exception as e:
        logger.error(f"Error fetching strategies: {e}")
    from backend.settings import get_settings
    return get_settings().model_strategies

@router.get(
    "/introspection", 
    summary="Introspect Agents",
    response_description="Discovery report."
)
def get_introspection():
    """Discover agents and schemas."""
    available_schemas = []
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            available_schemas.append(name)
    import pkgutil
    import importlib
    import backend.agents
    from backend.agents.base import BaseAgent
    available_agents = []
    available_hooks = set()
    package = backend.agents
    prefix = package.__name__ + "."
    for _, name, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        if name == "backend.agents.base": continue
        try:
            module = importlib.import_module(name)
            for cls_name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    available_agents.append(cls_name)
                    base_methods = set(dir(BaseAgent))
                    for method_name, method in inspect.getmembers(obj):
                        if (inspect.isfunction(method) or inspect.ismethod(method)) and not method_name.startswith('_'):
                             if method_name not in base_methods and method_name not in ['get_response_schema', 'execute']:
                                 available_hooks.add(f"{cls_name}.{method_name}")
        except Exception: continue
    return {"schemas": sorted(available_schemas), "agents": sorted(available_agents), "hooks": sorted(list(available_hooks))}

@router.post(
    "/validate-flow", 
    summary="Validate Flow",
    response_description="Validation Report."
)
def validate_flow(workflow: WorkflowCreate, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Dry run validation."""
    from backend.core.factory import AgentFactory
    try:
        agents_map = AgentFactory.create_agents_map(initial_model="gemini-1.5-flash")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Factory Error: {e}")
    
    known_keys = ["history_text", "product_text", "reflection_text", "bibliography_context"]
    errors = []
    trace_log = []
    all_steps_config = db.table('steps').all()
    steps_db_map = {s['id']: s for s in all_steps_config}
    pseudo_state = list(known_keys)

    for i, step_id in enumerate(workflow.sequence):
        if step_id not in steps_db_map:
            errors.append(f"Unknown Step: {step_id}")
            continue
        step_doc = steps_db_map[step_id]
        agent_name = step_doc.get('component')
        if not agent_name or agent_name not in agents_map:
             errors.append(f"Unknown Agent: {agent_name} in {step_id}")
             continue
        agent_instance = agents_map[agent_name]
        reqs = getattr(agent_instance, 'REQUIRES_KEYS', [])
        missing = [r for r in reqs if r not in pseudo_state]
        if missing:
             errors.append(f"Step {i+1} Missing: {missing}")
        prods = getattr(agent_instance, 'PRODUCES_KEYS', [])
        for k in prods:
            if k not in pseudo_state: pseudo_state.append(k)
                
    return {"valid": len(errors) == 0, "errors": errors, "trace": trace_log, "final_state_keys": pseudo_state}
