from fastapi import APIRouter, HTTPException, BackgroundTasks
from tinydb import TinyDB, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os

from backend.exporter import export_db_to_files
from backend.seeder import seed_database
from backend.config import DB_PATH, PROD_DB_PATH, MOCK_DB_PATH

router = APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

# Database Setup (Same as main.py)
# BASE_DIR and DATA_DIR are no longer needed here if we import DB_PATH

def get_db():
    return TinyDB(DB_PATH, encoding='utf-8')

# --- Models ---

class ComponentUpdate(BaseModel):
    content: str
    description: Optional[str] = None
    citation: Optional[str] = None
    citation_full: Optional[str] = None

class WorkflowUpdate(BaseModel):
    steps: Optional[List[Dict[str, Any]]] = None
    sequence: Optional[List[str]] = None
    description: Optional[str] = None
    default_model_mapping: Optional[Dict[str, str]] = None

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

class ComponentCreate(BaseModel):
    id: str
    name: str
    type: str
    content: str
    description: Optional[str] = None
    citation: Optional[str] = None
    citation_full: Optional[str] = None
    module: Optional[str] = "config"
    component_class: Optional[str] = "ConfigComponent" # Renamed from 'class' to avoid keyword conflict

@router.post("/components")
def create_component(comp: ComponentCreate):
    """Create a new component."""
    db = get_db()
    table = db.table('components')
    if table.search(Query().id == comp.id):
        raise HTTPException(status_code=400, detail="Component ID already exists")
    
    # Dump model to dict, handling aliasing if needed (but here simple dict is fine)
    new_comp = comp.dict()
    # Rename component_class back to class for storage if that's the convention, 
    # but 'class' is a reserved keyword in Python so pydantic model uses component_class.
    # Let's check how it's stored. The previous code used "class": "ConfigComponent".
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
        
    # Update by ID or Name
    table.update(update_data, (Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "updated", "id": comp_id}

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

class WorkflowCreate(BaseModel):
    id: str
    name: str
    sequence: List[str] = []
    description: Optional[str] = None
    default_model_mapping: Optional[Dict[str, str]] = {}

@router.post("/workflows")
def create_workflow(workflow: WorkflowCreate):
    """Create a new workflow."""
    db = get_db()
    Workflow = Query()
    table = db.table('workflows')
    
    if table.search(Workflow.id == workflow.id):
        raise HTTPException(status_code=400, detail="Workflow ID already exists")
        
    new_wf = workflow.dict()
    # Ensure sequence is saved as 'sequence' (and maybe 'steps' for compat if needed, but let's stick to sequence)
    # The engine looks for 'sequence' first.
    
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
    1. Exports current DB (Mock) to seed_data.json
    2. Resets Production DB from seed_data.json
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
    1. Exports current DB (Prod) to seed_data.json
    2. Resets Mock DB from seed_data.json
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
    Used for UI rendering and prompt expansion.
    """
    import inspect
    from backend import schemas
    
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
                print(f"Error processing schema {name}: {e}")
                
@router.get("/unified-prompts")
def get_unified_prompts():
    """
    Generates the Unified Master View text with schema expansion.
    """
    import json
    import re
    from backend import schemas
    import inspect

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
    comp_map = {c.get('id'): c for c in all_components if c.get('id')}

    # 4. Define Order
    ordered_ids = [
        "HEADER_MANDATES",
        "MANDATE_1_1", "MANDATE_1_2", "MANDATE_1_3", "MANDATE_1_4",
        "HEADER_RULES",
        "RULE_1", "RULE_2", "RULE_3", "RULE_4", "RULE_5", "RULE_6", "RULE_7", "RULE_8", "RULE_9", "RULE_10", "RULE_11", "RULE_12", "RULE_13", "RULE_14", "RULE_15",
        "BARS_MATRIX",
        "PROMPT_GUARD", "PROMPT_ANALYST", "PROMPT_LOGICIAN", "PROMPT_FALSIFIER", "PROMPT_CAUSAL", "PROMPT_PERFORMATIVITY", "PROMPT_FACT_CHECKER", "PROMPT_JUDGE", "PROMPT_XAI"
    ]

    # 5. Build Text
    unified_text = "# KOGNITIIVINEN KVOORUM - SYSTEM PROMPTS & SCHEMAS\n\n"
    for cid in ordered_ids:
        comp = comp_map.get(cid)
        if comp:
            unified_text += f"### {comp.get('id')} ({comp.get('type')})\n\n"
            raw_content = comp.get('content', '')
            expanded_content = expand_content(raw_content, schema_data)
            unified_text += f"{expanded_content}\n\n"
            unified_text += "---\n\n"
            
    return {"content": unified_text}
