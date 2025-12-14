from fastapi import APIRouter, HTTPException, BackgroundTasks
from tinydb import Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import json
import re
import inspect

from backend.database.exporter import export_db_to_files
from backend.database.seeder import seed_database
from backend.config import DB_PATH, PROD_DB_PATH, MOCK_DB_PATH, MODEL_STRATEGIES
from backend.database.wrapper import get_db_client
from backend.models import domain as schemas
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

def get_db():
    return get_db_client()

# --- Models ---

class ComponentUpdate(BaseModel):
    content: str
    description: Optional[str] = None
    citation: Optional[str] = None
    citation_full: Optional[str] = None

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
def get_components():
    """List all components (prompts, rules)."""
    db = get_db()
    return db.table('components').all()

@router.get("/components/{comp_id}")
def get_component(comp_id: str):
    """Get a specific component by ID."""
    db = get_db()
    Component = Query()
    # Try matching 'id' first, then 'name'
    res = db.table('components').search(Component.id == comp_id)
    if not res:
        res = db.table('components').search(Component.name == comp_id)
    
    if not res:
        raise HTTPException(status_code=404, detail="Component not found")
    return res[0]

@router.post("/components")
def create_component(comp: ComponentCreate):
    """Create a new component."""
    db = get_db()
    table = db.table('components')
    if table.search(Query().id == comp.id):
        raise HTTPException(status_code=400, detail="Component ID already exists")
    
    new_comp = comp.dict()
    if 'component_class' in new_comp:
        new_comp['class'] = new_comp.pop('component_class')
        
    table.insert(new_comp)
    return {"status": "created", "id": comp.id}

@router.put("/components/{comp_id}")
def update_component(comp_id: str, update: ComponentUpdate):
    """Update a component's content."""
    db = get_db()
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
        
    table.update(update_data, (Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "updated", "id": comp_id}

@router.delete("/components/{comp_id}")
def delete_component(comp_id: str):
    """Delete a component."""
    db = get_db()
    table = db.table('components')
    Component = Query()
    
    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        raise HTTPException(status_code=404, detail="Component not found")
        
    table.remove((Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "deleted", "id": comp_id}

@router.get("/steps")
def get_steps():
    """List all steps."""
    db = get_db()
    return db.table('steps').all()

@router.post("/steps")
def create_step(step: Dict[str, Any]):
    """Create a new step."""
    db = get_db()
    table = db.table('steps')
    if table.search(Query().id == step.get('id')):
        raise HTTPException(status_code=400, detail="Step ID already exists")
    table.insert(step)
    return {"status": "created", "id": step.get('id')}

@router.put("/steps/{step_id}")
def update_step(step_id: str, step: Dict[str, Any]):
    """Update a step."""
    db = get_db()
    table = db.table('steps')
    if not table.search(Query().id == step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    table.update(step, Query().id == step_id)
    return {"status": "updated", "id": step_id}

@router.delete("/steps/{step_id}")
def delete_step(step_id: str):
    """Delete a step."""
    db = get_db()
    table = db.table('steps')
    if not table.search(Query().id == step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    table.remove(Query().id == step_id)
    return {"status": "deleted", "id": step_id}

@router.get("/workflows")
def get_workflows():
    """List all workflows."""
    db = get_db()
    return db.table('workflows').all()

@router.get("/workflows/{wf_id}")
def get_workflow(wf_id: str):
    """Get a specific workflow."""
    db = get_db()
    Workflow = Query()
    res = db.table('workflows').search(Workflow.id == wf_id)
    if not res:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return res[0]

@router.put("/workflows/{wf_id}")
def update_workflow(wf_id: str, update: WorkflowUpdate):
    """Update a workflow definition."""
    db = get_db()
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

    table.update(update_data, Workflow.id == wf_id)
    return {"status": "updated", "id": wf_id}

@router.post("/workflows")
def create_workflow(workflow: WorkflowCreate):
    """Create a new workflow."""
    db = get_db()
    Workflow = Query()
    table = db.table('workflows')
    
    if table.search(Workflow.id == workflow.id):
        raise HTTPException(status_code=400, detail="Workflow ID already exists")
        
    new_wf = workflow.dict()
    table.insert(new_wf)
    return {"status": "created", "id": workflow.id}

@router.delete("/workflows/{wf_id}")
def delete_workflow(wf_id: str):
    """Delete a workflow."""
    db = get_db()
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
    try:
        # 1. Export Mock DB to seed_data.json
        export_db_to_files(source_db_path=MOCK_DB_PATH)
        
        # 2. Seed Production DB from the updated seed file
        seed_database(target_db_path=PROD_DB_PATH)
        
        return {"status": "success", "message": "Mock environment deployed to Production DB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy-prod-to-mock")
def deploy_prod_to_mock():
    """
    Deploys the current Production environment configuration to the Mock Database.
    """
    try:
        # 1. Export Prod DB to seed_data.json
        export_db_to_files(source_db_path=PROD_DB_PATH)
        
        # 2. Seed Mock DB from the updated seed file
        seed_database(target_db_path=MOCK_DB_PATH)
        
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
def get_unified_prompts():
    """
    Generates the Unified Master View text with schema expansion.
    """
    # 1. Fetch Schemas
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

    # 2. Define Expansion Logic
    def expand_content(text, schemas):
        if not text: return ""
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

    # 3. Fetch Components
    db = get_db()
    all_components = db.table('components').all()
    
    # Group by type
    grouped = {}
    for c in all_components:
        ctype = c.get('type', 'other')
        if ctype not in grouped:
            grouped[ctype] = []
        grouped[ctype].append(c)
        
    # Define Type Order
    type_order = ["header", "mandate", "rule", "principle", "protocol", "method", "heuristic", "requirement", "prompt"]
    
    # 5. Build Text
    unified_text = "# KOGNITIIVINEN KVOORUM - SYSTEM PROMPTS & SCHEMAS\n\n"
    
    for ctype in type_order:
        if ctype in grouped:
            comps = sorted(grouped[ctype], key=lambda x: str(x.get('id') or ''))
            for comp in comps:
                unified_text += f"### {comp.get('id')} ({comp.get('type')})\n\n"
                raw_content = comp.get('content', '')
                expanded_content = expand_content(raw_content, schema_data)
                unified_text += f"{expanded_content}\n\n"
                unified_text += "---\n\n"
                
    # Add any remaining types
    for ctype, comps in grouped.items():
        if ctype not in type_order:
             comps = sorted(comps, key=lambda x: str(x.get('id') or ''))
             for comp in comps:
                unified_text += f"### {comp.get('id')} ({comp.get('type')})\n\n"
                raw_content = comp.get('content', '')
                expanded_content = expand_content(raw_content, schema_data)
                unified_text += f"{expanded_content}\n\n"
                unified_text += "---\n\n"

    return {"content": unified_text}

@router.get("/models/registry")
def get_model_registry():
    """
    Get the global model registry from system_config.
    """
    db = get_db_client()
    table = db.table('system_config')
    Config = Query()
    res = table.search(Config.type == 'model_registry')
    if res:
        return res[0].get('models', {})
    return {}

@router.post("/models/registry")
def update_model_registry(config: GlobalModelConfig):
    """
    Update the global model registry.
    """
    db = get_db_client()
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
def get_model_strategies():
    """
    Get the available model strategies (Fast vs Deep).
    Prioritizes DB config 'model_registry' > 'google' provider.
    Fallback to static MODEL_STRATEGIES.
    """
    # 1. Try fetching from DB
    try:
        db = get_db_client()
        table = db.table('system_config')
        Config = Query()
        res = table.search(Config.type == 'model_registry')
        if res and 'models' in res[0]:
            registry = res[0]['models']
            # Default to google for now as it's the main provider
            if 'google' in registry:
                return registry['google']
    except Exception as e:
        logger.error(f"Error fetching strategies from DB: {e}")

    # 2. Fallback to static
    return MODEL_STRATEGIES

@router.get("/introspection")
def get_introspection():
    """
    Introspects the backend to return available Schemas, Hooks, and Agents.
    """
    # 1. Schemas
    available_schemas = []
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            available_schemas.append(name)
            
    # 2. Agents & Hooks
    import backend.agents.guard as guard_agent
    import backend.agents.analyst as analyst_agent
    import backend.agents.logician as logician_agent
    import backend.agents.critics as critics_agent
    import backend.agents.judge as judge_agent
    import backend.agents.xai as xai_agent
    from backend.agents.base import BaseAgent
    
    agent_modules = [guard_agent, analyst_agent, logician_agent, critics_agent, judge_agent, xai_agent]
    available_agents = []
    available_hooks = set()
    
    for module in agent_modules:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                available_agents.append(name)
                
                # Inspect methods for hooks
                for method_name, method in inspect.getmembers(obj):
                    if inspect.isfunction(method) or inspect.ismethod(method):
                        # Filter out dunder methods and private methods
                        if not method_name.startswith('_'):
                            # Filter out BaseAgent methods that aren't really hooks
                            if method_name not in ['execute', 'get_response_schema', 'run', 'get_output_schema_name']:
                                available_hooks.add(method_name)
                                
    return {
        "schemas": sorted(available_schemas),
        "agents": sorted(available_agents),
        "hooks": sorted(list(available_hooks))
    }
