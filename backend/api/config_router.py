from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from tinydb import Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import json
import re
import inspect

from backend.database.exporter import export_db_to_files
from backend.database.seeder import seed_database
# from backend.config import DB_PATH, PROD_DB_PATH, MOCK_DB_PATH, MODEL_STRATEGIES # Removed
from backend.database.wrapper import get_db_client, AbstractDatabase
from backend.dependencies import get_db_client_dep
from backend.models import domain as schemas
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/config",
    tags=["Configuration"]
)



# --- Models ---

class ComponentUpdate(BaseModel):
    content: str
    description: Optional[str] = None
    citation: Optional[str] = None
    citation_full: Optional[str] = None
    type: Optional[str] = None

class ModelSettings(BaseModel):
    model_name: str
    temperature: Optional[float] = Field(None)
    max_tokens: Optional[int] = Field(None)
    top_p: Optional[float] = Field(None)

class GlobalModelConfig(BaseModel):
    registry: Dict[str, Dict[str, ModelSettings]]

class WorkflowUpdate(BaseModel):
    steps: Optional[List[Dict[str, Any]]] = None
    sequence: Optional[List[str]] = None
    description: Optional[str] = None
    default_model_mapping: Optional[Dict[str, str]] = None

class ComponentCreate(BaseModel):
    id: str
    name: str
    type: str
    content: str
    description: Optional[str] = None
    citation: Optional[str] = None
    citation_full: Optional[str] = None
    module: Optional[str] = "config"
    component_class: Optional[str] = "ConfigComponent" 

class WorkflowCreate(BaseModel):
    id: str
    name: str
    sequence: List[str] = []
    description: Optional[str] = None
    default_model_mapping: Optional[Dict[str, str]] = {}

# --- Endpoints ---

@router.get("/components")
def get_components(db: AbstractDatabase = Depends(get_db_client_dep)):
    """List all components (prompts, rules)."""
    return db.table('components').all()

@router.get("/components/{comp_id}")
def get_component(comp_id: str, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Get a specific component by ID."""
    Component = Query()
    # Try matching 'id' first, then 'name'
    res = db.table('components').search(Component.id == comp_id)
    if not res:
        res = db.table('components').search(Component.name == comp_id)
    
    if not res:
        raise HTTPException(status_code=404, detail="Component not found")
    return res[0]

@router.post("/components")
def create_component(comp: ComponentCreate, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Create a new component."""
    table = db.table('components')
    if table.search(Query().id == comp.id):
        raise HTTPException(status_code=400, detail="Component ID already exists")
    
    new_comp = comp.model_dump()
    if 'component_class' in new_comp:
        new_comp['class'] = new_comp.pop('component_class')
        
    table.insert(new_comp)
    return {"status": "created", "id": comp.id}

@router.put("/components/{comp_id}")
def update_component(comp_id: str, update: ComponentUpdate, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Update a component's content."""
    Component = Query()
    table = db.table('components')
    
    # Check existence
    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Update
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

@router.delete("/components/{comp_id}")
def delete_component(comp_id: str, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Delete a component."""
    table = db.table('components')
    Component = Query()
    
    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Referential Integrity Check
    steps = db.table('steps').all()
    used_in = []
    
    for s in steps:
        # Check 1: Is this component the Agent Logic for the step?
        if s.get('component') == comp_id:
            used_in.append(s['id'])
            continue
            
        # Check 2: Is this component in the prompt list?
        prompts = s.get('execution_config', {}).get('llm_prompts', [])
        if comp_id in prompts:
            used_in.append(s['id'])
            
    if used_in:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete component '{comp_id}'. It is used in {len(used_in)} steps: {', '.join(used_in[:3])}..."
        )
        
    table.remove((Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "deleted", "id": comp_id}

@router.get("/steps")
def get_steps(db: AbstractDatabase = Depends(get_db_client_dep)):
    """List all steps."""
    return db.table('steps').all()

@router.post("/steps")
def create_step(step: Dict[str, Any], db: AbstractDatabase = Depends(get_db_client_dep)):
    """Create a new step."""
    table = db.table('steps')
    if table.search(Query().id == step.get('id')):
        raise HTTPException(status_code=400, detail="Step ID already exists")
    table.insert(step)
    return {"status": "created", "id": step.get('id')}

@router.put("/steps/{step_id}")
def update_step(step_id: str, step: Dict[str, Any], db: AbstractDatabase = Depends(get_db_client_dep)):
    """Update a step."""
    table = db.table('steps')
    if not table.search(Query().id == step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    table.update(step, Query().id == step_id)
    return {"status": "updated", "id": step_id}

@router.delete("/steps/{step_id}")
def delete_step(step_id: str, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Delete a step."""
    table = db.table('steps')
    if not table.search(Query().id == step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    table.remove(Query().id == step_id)
    return {"status": "deleted", "id": step_id}

@router.get("/workflows")
def get_workflows(db: AbstractDatabase = Depends(get_db_client_dep)):
    """List all workflows."""
    return db.table('workflows').all()

@router.get("/workflows/{wf_id}")
def get_workflow(wf_id: str, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Get a specific workflow."""
    Workflow = Query()
    res = db.table('workflows').search(Workflow.id == wf_id)
    if not res:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return res[0]

@router.put("/workflows/{wf_id}")
def update_workflow(wf_id: str, update: WorkflowUpdate, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Update a workflow definition."""
    Workflow = Query()
    table = db.table('workflows')
    
    if not table.search(Workflow.id == wf_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    update_data = {}
    if update.steps is not None:
        update_data["steps"] = update.steps
    if update.sequence is not None:
        update_data["sequence"] = update.sequence
    if update.description:
        update_data["description"] = update.description
    if update.default_model_mapping is not None:
        update_data["default_model_mapping"] = update.default_model_mapping
        
    if not update_data:
         raise HTTPException(status_code=400, detail="No data to update")

    # Validation: Check if referenced steps exist (if creating/updating sequence)
    # Note: 'sequence' in JSON model corresponds to 'steps' list in DB logic for some reason, 
    # but based on seed_data it is 'steps'. Currently the model uses 'sequence'.
    # Let's check update.sequence or update.steps depending on what Pydantic model uses.
    # The Pydantic model 'WorkflowUpdate' has 'steps' and 'sequence'. 
    # In seed_data it is 'steps'. Let's validate whichever list is provided.
    
    steps_to_check = update.steps if update.steps else update.sequence
    
    if steps_to_check:
        valid_steps = {s['id'] for s in db.table('steps').all()}
        # steps_to_check might be a list of strings (IDs) or dicts?
        # In seed_data 'steps' is a list of strings.
        for item in steps_to_check:
            # Handle if item is string or dict (though Config View sends list of strings)
            sid = item if isinstance(item, str) else item.get('id')
            if sid and sid not in valid_steps:
                 raise HTTPException(status_code=400, detail=f"Invalid Step ID: '{sid}' does not exist.")

    table.update(update_data, Workflow.id == wf_id)
    return {"status": "updated", "id": wf_id}

@router.post("/workflows")
def create_workflow(workflow: WorkflowCreate, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Create a new workflow."""
    Workflow = Query()
    table = db.table('workflows')
    
    if table.search(Workflow.id == workflow.id):
        raise HTTPException(status_code=400, detail="Workflow ID already exists")
        
    new_wf = workflow.model_dump()
    
    # Validation: Check if referenced steps exist
    if workflow.sequence:
        valid_steps = {s['id'] for s in db.table('steps').all()}
        for step_id in workflow.sequence:
            if step_id not in valid_steps:
                 raise HTTPException(status_code=400, detail=f"Invalid Step ID: '{step_id}' does not exist.")

    table.insert(new_wf)
    return {"status": "created", "id": workflow.id}

@router.delete("/workflows/{wf_id}")
def delete_workflow(wf_id: str, db: AbstractDatabase = Depends(get_db_client_dep)):
    """Delete a workflow."""
    Workflow = Query()
    table = db.table('workflows')
    
    if not table.search(Workflow.id == wf_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    table.remove(Workflow.id == wf_id)
    return {"status": "deleted", "id": wf_id}

@router.post("/export-seed")
def export_seed_data(background_tasks: BackgroundTasks):
    """Trigger an export of the database to the file system."""
    background_tasks.add_task(export_db_to_files)
    return {"status": "export_started", "message": "Exporting DB to files in background."}

@router.post("/reset-from-seed")
def reset_from_seed():
    """Reset the database from the seed data file."""
    try:
        seed_database()
        return {"status": "success", "message": "Database reset from seed data."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy-mock-to-prod")
def deploy_mock_to_prod():
    """
    Deploys the current Mock environment configuration to the Production Database.
    """
    from backend.settings import get_settings
    settings = get_settings()
    try:
        # 1. Export Mock DB to seed_data.json
        export_db_to_files(source_db_path=settings.mock_db_path)
        
        # 2. Seed Production DB from the updated seed file
        seed_database(target_db_path=settings.prod_db_path)
        
        return {"status": "success", "message": "Mock environment deployed to Production DB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy-prod-to-mock")
def deploy_prod_to_mock():
    """
    Deploys the current Production environment configuration to the Mock Database.
    """
    from backend.settings import get_settings
    settings = get_settings()
    try:
        # 1. Export Prod DB to seed_data.json
        export_db_to_files(source_db_path=settings.prod_db_path)
        
        # 2. Seed Mock DB from the updated seed file
        seed_database(target_db_path=settings.mock_db_path)
        
        return {"status": "success", "message": "Production environment deployed to Mock DB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemas")
def get_schemas():
    """
    Returns a dictionary of all available schemas and their examples.
    """
    schema_data = {}
    
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            try:
                # Get JSON Schema
                json_schema = obj.model_json_schema()
                
                # Get Example from ConfigDict if available
                example = None
                if hasattr(obj, 'model_config'):
                    config = obj.model_config
                    if 'json_schema_extra' in config:
                        extra = config['json_schema_extra']
                        if 'examples' in extra and extra['examples']:
                            example = extra['examples'][0]
                
                schema_data[name] = {
                    "schema": json_schema,
                    "example": example
                }
            except Exception as e:
                logger.error(f"Error processing schema {name}: {e}")
    return schema_data

@router.get("/unified-prompts")
def get_unified_prompts(db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Generates the Unified Master View text with schema expansion.
    Refactored to use helper functions for clarity.
    """
    try:
        # 1. Fetch Schema Data
        schema_data = _fetch_schemas()

        # 2. Fetch Components
        all_components = db.table('components').all()
        
        # 3. Build Text
        unified_text = _build_unified_view(all_components, schema_data)
        
        return {"content": unified_text}
    except Exception as e:
        logger.error(f"Error generating unified prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _fetch_schemas() -> Dict[str, Any]:
    """Helper to fetch and parse Pydantic schemas."""
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
            except Exception:
                pass
    return schema_data

def _expand_content(text: Any, schemas: Dict[str, Any]) -> str:
    """Helper to expand placeholders in text with schema examples/definitions."""
    if not text: return ""
    
    # Handle non-string input safely
    if isinstance(text, list):
        text = "\n".join(str(x) for x in text)
    if not isinstance(text, str):
        text = str(text)
    
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
    """Helper to construct the unified markdown text."""
    
    # Group by type
    grouped = {}
    for c in components:
        ctype = c.get('type', 'other')
        if ctype not in grouped:
            grouped[ctype] = []
        grouped[ctype].append(c)
        
    type_order = ["header", "mandate", "rule", "principle", "protocol", "method", "heuristic", "requirement", "prompt"]
    
    unified_text = "# KOGNITIIVINEN KVOORUM - SYSTEM PROMPTS & SCHEMAS\n\n"
    
    # Helper to process a list of components
    def process_comp_list(comps):
        text = ""
        # Sort by ID
        sorted_comps = sorted(comps, key=lambda x: str(x.get('id') or ''))
        for comp in sorted_comps:
            text += f"### {comp.get('id')} ({comp.get('type')})\n\n"
            raw_content = comp.get('content', '')
            expanded_content = _expand_content(raw_content, schema_data)
            text += f"{expanded_content}\n\n"
            text += "---\n\n"
        return text

    # Process ordered types first
    for ctype in type_order:
        if ctype in grouped:
            unified_text += process_comp_list(grouped[ctype])
                
    # Add any remaining types
    for ctype, comps in grouped.items():
        if ctype not in type_order:
            unified_text += process_comp_list(comps)
            
    return unified_text

@router.get("/models/registry")
def get_model_registry(db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Get the global model registry from system_config.
    """
    table = db.table('system_config')
    Config = Query()
    res = table.search(Config.type == 'model_registry')
    if res:
        return res[0].get('models', {})
    return {}

@router.post("/models/registry")
def update_model_registry(config: GlobalModelConfig, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Update the global model registry.
    """
    table = db.table('system_config')
    Config = Query()
    
    # Serialize to dict for TinyDB
    if hasattr(config, 'model_dump_json'):
        raw_json = config.model_dump_json()
    else:
        raw_json = config.json()
        
    registry_data = json.loads(raw_json)['registry']
    
    table.upsert(
        {
            'type': 'model_registry',
            'models': registry_data
        },
        Config.type == 'model_registry'
    )
    return {"status": "updated", "registry": registry_data}

@router.get("/models/strategies")
def get_model_strategies(db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Get the available model strategies (Fast vs Deep).
    Prioritizes DB config 'model_registry' > 'google' > 'openai'.
    Fallback to static MODEL_STRATEGIES from settings.
    """
    logger.info("Fetching model strategies...")
    # 1. Try fetching from DB
    try:
        table = db.table('system_config')
        Config = Query()
        res = table.search(Config.type == 'model_registry')
        
        if res and 'models' in res[0]:
            registry = res[0]['models']
            
            # Prioritize Google, then OpenAI
            if 'google' in registry and registry['google']:
                logger.debug(f"Returning Google strategies from DB: {registry['google']}")
                return registry['google']
            
            if 'openai' in registry and registry['openai']:
                 logger.debug(f"Returning OpenAI strategies from DB: {registry['openai']}")
                 return registry['openai']
                 
    except Exception as e:
        logger.error(f"Error fetching strategies from DB: {e}")

    # 2. Fallback to static
    from backend.settings import get_settings
    settings = get_settings()
    logger.debug(f"Returning default settings strategies: {settings.model_strategies}")
    return settings.model_strategies

@router.get("/introspection")
def get_introspection():
    """
    Introspects the backend to return available Schemas and Agents.
    """
    # 1. Schemas
    available_schemas = []
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            available_schemas.append(name)
            
    # 2. Agents (Dynamic Discovery)
    import pkgutil
    import importlib
    import backend.agents
    from backend.agents.base import BaseAgent
    
    available_agents = []
    available_hooks = set()
    
    # Iterate over all modules in backend.agents package
    package = backend.agents
    prefix = package.__name__ + "."
    
    for _, name, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        if name == "backend.agents.base": continue # Skip base
        
        try:
            module = importlib.import_module(name)
            
            for cls_name, obj in inspect.getmembers(module):
                # Find classes that inherit from BaseAgent
                if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    available_agents.append(cls_name)
                    
                    # Inspect methods for hooks (public methods not defined in BaseAgent)
                    # Note: With V2 architecture, hooks are just methods.
                    # We expose them for clarity/documentation if needed.
                    base_methods = set(dir(BaseAgent))
                    
                    for method_name, method in inspect.getmembers(obj):
                        if inspect.isfunction(method) or inspect.ismethod(method):
                            if not method_name.startswith('_'):
                                if method_name not in base_methods and method_name not in ['get_response_schema', 'execute']:
                                     # It's likely a custom hook/method
                                     available_hooks.add(f"{cls_name}.{method_name}")

        except Exception as e:
            logger.warning(f"Failed to introspect module {name}: {e}")
            continue
                                
    return {
        "schemas": sorted(available_schemas),
        "agents": sorted(available_agents),
        "hooks": sorted(list(available_hooks))
    }

@router.post("/validate-flow")
def validate_flow(workflow: WorkflowCreate, db: AbstractDatabase = Depends(get_db_client_dep)):
    """
    Performs a Data Flow Validation (Dry Run) on the proposed workflow.
    CHECKS:
    1. Do referenced steps exist?
    2. Does the agent component exist?
    3. Are REQUIRED_KEYS satisfied by the cumulative state?
    """
    from backend.core.factory import AgentFactory
    
    # Introspect available agents (lightweight instantiation)
    # Using 'fast' as dummy model just for instantiation
    try:
        agents_map = AgentFactory.create_agents_map(initial_model="gemini-1.5-flash") # Model doesn't matter for contracts
    except Exception as e:
        logger.error(f"Validation failed during factory init: {e}")
        raise HTTPException(status_code=500, detail=f"Agent Factory Error: {e}")
    
    # 0. Initial State (Simulated)
    # We assume standard Inputs are present
    known_keys = ["history_text", "product_text", "reflection_text", "bibliography_context"]
    
    errors = []
    trace_log = []
    
    # Load Steps Config
    all_steps_config = db.table('steps').all()
    steps_db_map = {s['id']: s for s in all_steps_config}
    
    pseudo_state = list(known_keys)

    for i, step_id in enumerate(workflow.sequence):
        # 1. Resolve Step
        if step_id not in steps_db_map:
            msg = f"Step '{step_id}' references unknown step ID."
            errors.append(msg)
            trace_log.append(f"❌ {msg}")
            continue
            
        step_doc = steps_db_map[step_id]
        agent_name = step_doc.get('component')
        
        # 2. Resolve Agent Class
        if not agent_name or agent_name not in agents_map:
             msg = f"Step '{step_id}' uses unknown Agent component '{agent_name}'."
             errors.append(msg)
             trace_log.append(f"❌ {msg}")
             continue
             
        agent_instance = agents_map[agent_name]
        
        # 3. Check Requirements (Level 1)
        reqs = getattr(agent_instance, 'REQUIRES_KEYS', [])
        missing = []
        for req in reqs:
            if req not in pseudo_state:
                missing.append(req)
        
        if missing:
             # Critical Error
             err_msg = f"Step {i+1} ({step_id}/{agent_name}) MISSING INPUTS: {missing}. Available keys: {pseudo_state}"
             errors.append(err_msg)
             trace_log.append(f"❌ [Step {i+1}] {err_msg}")
        else:
             trace_log.append(f"✅ [Step {i+1}: {step_id}] Inputs OK.")

        # 4. Simulate Production
        prods = getattr(agent_instance, 'PRODUCES_KEYS', [])
        for k in prods:
            if k not in pseudo_state:
                pseudo_state.append(k)
        
        if prods:
            trace_log.append(f"   -> Produced: {prods}")
                
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "trace": trace_log,
        "final_state_keys": pseudo_state
    }
