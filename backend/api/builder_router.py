from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import uuid
import copy
from datetime import datetime

from backend.dependencies import get_engine
from backend.core.engine import WorkflowEngine
from backend.services.agent_registry import AgentRegistry

router = APIRouter(
    prefix="/builder",
    tags=["Builder"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

# --- Models ---
class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[str]  # List of step IDs in order
    ui_schema: Optional[Dict[str, Any]] = None # UI coordinates
    default_model_mapping: Optional[Dict[str, str]] = None

class WorkflowUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[str]] = None
    ui_schema: Optional[Dict[str, Any]] = None
    default_model_mapping: Optional[Dict[str, str]] = None

class CopyWorkflowRequest(BaseModel):
    new_name: str

class ValidationRequest(BaseModel):
    source_step: str
    target_step: str

class WorkflowTemplate(BaseModel):
    name: str
    description: str = ""
    steps: List[str] = []
    default_model_mapping: Dict[str, str] = {}
    ui_schema: Dict[str, Any] = {"nodes": []}


# --- Helpers ---

def _get_orphan_steps(repo, workflow_id: str) -> List[str]:
    """Identify steps used ONLY by the given workflow."""
    target_wf = repo.get_workflow_by_id(workflow_id)
    if not target_wf:
        return []
    
    target_steps = set(target_wf.get('steps', []))
    used_elsewhere = set()
    
    all_wfs = repo.get_all_workflows()
    for wf in all_wfs:
        if wf['id'] == workflow_id:
            continue
        for step_id in wf.get('steps', []):
            used_elsewhere.add(step_id)
            
    orphans = target_steps - used_elsewhere
    return list(orphans)

# --- Endpoints ---

@router.get("/config/agents")
async def get_available_agents(engine: WorkflowEngine = Depends(get_engine)):
    """
    Discovery: Returns metadata for all registered agents.
    Used for the Builder Toolbox.
    """
    try:
        registry = engine.registry
        agents_meta = []
        
        # registry.agents_map is Dict[str, BaseAgent] (Instances)
        # Use get_all_agents() for safety
        agents = registry.get_all_agents()
        
        for name, agent_inst in agents.items():
            # Get class docstring
            agent_cls = agent_inst.__class__
            
            meta = {
                "name": name,
                "description": agent_cls.__doc__ or "No description.",
                "inputs": getattr(agent_cls, "INPUT_REQUIREMENTS", []),
                "outputs": []
            }
            
            # Check for schemas
            if hasattr(agent_inst, "get_response_schema"):
                 # We might want serialize
                 pass
            
            agents_meta.append(meta)
                
        return agents_meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows")
async def list_workflows(engine: WorkflowEngine = Depends(get_engine)):
    """List all workflows for the dashboard."""
    return engine.repository.get_all_workflows()

@router.post("/workflows")
async def create_workflow(request: WorkflowCreateRequest, engine: WorkflowEngine = Depends(get_engine)):
    """Create a new workflow."""
    try:
        new_id = str(uuid.uuid4()).split('-')[0] # Short ID
        workflow_data = {
            "id": f"wf_{new_id}", # custom ID format
            "name": request.name,
            "description": request.description or "",
            "steps": request.steps,
            "default_model_mapping": request.default_model_mapping or {},
            "ui_schema": request.ui_schema or {}, # Store visual layout
            "created_at": datetime.now().isoformat()
        }
        
        # We need a direct method in repository to add workflow with custom ID
        # The engine.create_workflow returns an ID but might enforce its own logic.
        # Let's use the repository directly.
        engine.repository.db.table('workflows').insert(workflow_data)
        
        return workflow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """Get details of a specific workflow."""
    wf = engine.repository.get_workflow_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf

@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, request: WorkflowUpdateRequest, engine: WorkflowEngine = Depends(get_engine)):
    """Update an existing workflow."""
    wf = engine.repository.get_workflow_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    update_data = {}
    if request.name is not None: update_data['name'] = request.name
    if request.description is not None: update_data['description'] = request.description
    if request.steps is not None: update_data['steps'] = request.steps
    if request.ui_schema is not None: update_data['ui_schema'] = request.ui_schema
    if request.default_model_mapping is not None: update_data['default_model_mapping'] = request.default_model_mapping
    
    update_data['updated_at'] = datetime.now().isoformat()
    
    # Use repo update
    # Note: Repository abstract method might be limited, accessing DB directly for custom fields if needed
    # But let's try standard update if available
    # engine.repository.update_workflow(workflow_id, update_data) # Does not exist in abstract?
    
    # Fallback to direct DB access for generic update
    from tinydb import Query
    Layout = Query()
    engine.repository.db.table('workflows').update(update_data, Layout.id == workflow_id)
    
    return {**wf, **update_data}

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """
    Delete a workflow AND its orphan steps (Garbage Collection).
    """
    wf = engine.repository.get_workflow_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # 1. Identify Orphan Steps
    orphans = _get_orphan_steps(engine.repository, workflow_id)
    
    # 2. Delete Workflow
    from tinydb import Query
    WF = Query()
    engine.repository.db.table('workflows').remove(WF.id == workflow_id)
    
    # 3. Delete Orphans
    Step = Query()
    deleted_steps = []
    for step_id in orphans:
        engine.repository.db.table('steps').remove(Step.id == step_id)
        deleted_steps.append(step_id)
        
    logger.info(f"Deleted workflow {workflow_id} and orphan steps: {deleted_steps}")
    
    return {"status": "deleted", "deleted_steps": deleted_steps}

@router.post("/workflows/{workflow_id}/copy")
async def copy_workflow(workflow_id: str, request: CopyWorkflowRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    Deep Copy a workflow.
    Currently references the SAME steps (Shallow Step Copy), but ideally should optionaly deep copy steps.
    For V1: References same steps logic is safer to avoid explosion, 
    BUT as per requirement we might want 'Copy-on-Write' later.
    """
    original = engine.repository.get_workflow_by_id(workflow_id)
    if not original:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    new_id = f"{original['id']}_copy_{uuid.uuid4().hex[:4]}"
    
    new_wf = copy.deepcopy(original)
    new_wf['id'] = new_id
    new_wf['name'] = request.new_name
    new_wf['created_at'] = datetime.now().isoformat()
    if 'updated_at' in new_wf: del new_wf['updated_at']
    
    # Convert to pure dict to detach from TinyDB Document type
    # This prevents 'Document with ID X already exists' errors if deepcopy preserved metadata
    clean_wf = dict(new_wf)
    
    try:
        # Insert
        engine.repository.db.table('workflows').insert(clean_wf)
        return clean_wf
    except Exception as e:
        logger.error(f"Copy workflow failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Copy failed: {str(e)}")

@router.post("/validate")
async def validate_connection(request: ValidationRequest):
    """
    Stub for validating connections between steps.
    """
    # Logic to fetch steps and check I/O compatibility
    return {"valid": True, "reason": "Validation not fully implemented yet."}

class CompileRequest(BaseModel):
    workflow_id: str
    steps: List[str]



# --- V2: Step Configuration ---

@router.get("/steps/{step_id}")
async def get_step_details(step_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """V2: Get full configuration of a step."""
    step = engine.repository.get_step_by_id(step_id)
    if not step:
         raise HTTPException(status_code=404, detail="Step not found")
    return step

class StepUpdateRequest(BaseModel):
    name: Optional[str] = None
    execution_config: Optional[Dict[str, Any]] = None # {"llm_prompts": [...]}

@router.put("/steps/{step_id}")
async def update_step(step_id: str, request: StepUpdateRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    V2: Update a step configuration.
    WARNING: This modifies the global step definition.
    Use with caution or for Custom Steps only.
    """
    from tinydb import Query
    
    step = engine.repository.get_step_by_id(step_id)
    if not step:
         raise HTTPException(status_code=404, detail="Step not found")
         
    update_data = {}
    if request.name is not None: update_data['name'] = request.name
    if request.execution_config is not None: update_data['execution_config'] = request.execution_config
    
    Step = Query()
    engine.repository.db.table('steps').update(update_data, Step.id == step_id)
    
    return {**step, **update_data}

@router.post("/steps/clone")
async def clone_step(source_step_id: str = Body(..., embed=True), engine: WorkflowEngine = Depends(get_engine)):
    """
    V2: Clone a step to a new Custom Step (Copy-on-Write).
    Returns the new step ID.
    """
    step = engine.repository.get_step_by_id(source_step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Source step not found")
        
    new_id = f"{source_step_id}_custom_{uuid.uuid4().hex[:6]}"
    new_step = copy.deepcopy(step)
    new_step['id'] = new_id
    new_step['name'] = f"{step.get('name')} (Custom)"
    
    # Convert to pure dict
    clean_step = dict(new_step)
    
    engine.repository.db.table('steps').insert(clean_step)
    
    engine.repository.db.table('steps').insert(clean_step)
    
    return clean_step

@router.get("/utils/generate-id")
async def generate_id(prefix: str = "custom_step"):
    """Generates a unique ID with optional prefix."""
    return {"id": f"{prefix}_{uuid.uuid4().hex[:6]}"}


@router.get("/config/template")
async def get_workflow_template():
    """Returns a valid empty workflow template."""
    return WorkflowTemplate(
        name="New Workflow",
        description="",
        steps=[],
        default_model_mapping={},
        ui_schema={"nodes": []}
    )

@router.get("/config/fusion-rules")
async def get_fusion_rules(engine: WorkflowEngine = Depends(get_engine)):
    """
    Returns validation rules for prompt fusion.
    Scans available steps for those with 'fusion_info'.
    """
    rules = []
    # Scan steps table (seed steps usually carry this info)
    all_steps = engine.repository.db.table('steps').all()
    for s in all_steps:
        if 'fusion_info' in s:
            rules.append({
                "composite_step_id": s['id'],
                "name": s.get('name', s['id']),
                "replaces_components": s['fusion_info'].get('replaces_components', []),
                "min_steps": s['fusion_info'].get('min_steps', 2)
            })
    return rules

@router.get("/config/prompt-types")
async def get_prompt_types():
    """Returns list of component types that can be used as prompts."""
    return ["prompt", "mandate", "rule", "header", "instruction"]

@router.post("/compile")

@router.post("/compile")
async def compile_fusion(req: CompileRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    V2: Prompt Fusion Compilation.
    Replaces a sequence of steps with a compatible Composite Step (Panel).
    Validates compatibility using 'fusion_info'.
    """
    wf = engine.repository.get_workflow_by_id(req.workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    current_steps = wf.get('steps', [])
    steps_to_fuse = req.steps
    
    # 1. Validation: Are steps present?
    if not all(s in current_steps for s in steps_to_fuse):
        raise HTTPException(status_code=400, detail="One or more steps not found in workflow")

    # 2. Find Composite Candidate
    # For V1, we assume target is 'step_panel', but let's be dynamic.
    # We look for a step definition that claims to replace these components.
    
    # Get component types of the steps to be fused
    fusing_components = []
    step_map = {s['id']: s for s in engine.repository.db.table('steps').all()} # Cache for speed
    
    for sid in steps_to_fuse:
        s_def = step_map.get(sid)
        if s_def:
            fusing_components.append(s_def.get('component'))
        else:
             # Handle custom steps or missing defs - strict mode would fail
             pass
    
    # Find a rule that covers these components
    target_composite_id = "step_panel" # Default fallback
    valid_fusion = False
    
    all_steps = step_map.values()
    for s in all_steps:
        if 'fusion_info' in s:
            allowed = set(s['fusion_info'].get('replaces_components', []))
            # Check if ALL fusing components are in the allowed list
            if fusing_components and all(comp in allowed for comp in fusing_components):
                target_composite_id = s['id']
                valid_fusion = True
                break
    
    # If not strictly validated via metadata, check hardcoded fallback for backward compat
    if not valid_fusion:
        # Fallback: Just allow it if it looks like the old list (Safety check)
        # Or if we want strict mode:
        # raise HTTPException(400, "Selected steps are not compatible for fusion.")
        logger.warning(f"Fusion validation weak for steps: {steps_to_fuse}. Defaulting to step_panel.")
    
    # Logic: Find the FIRST index of the fuse group, remove them all, insert target
    # 1. Identify indices
    indices = sorted([current_steps.index(s) for s in steps_to_fuse])
    first_idx = indices[0]
    
    # 2. Filter out fused steps
    new_steps = [s for s in current_steps if s not in steps_to_fuse]
    
    # 3. Insert target composite step at the position of the first removed step
    new_steps.insert(first_idx, target_composite_id)
    
    # Update Model Mapping
    mapping = wf.get('default_model_mapping', {}).copy()
    
    # Remove old keys
    for step_id in steps_to_fuse:
        if step_id in mapping:
            del mapping[step_id]
            
    # Add new key (Hardcoded DEEP for Panel as per design)
    mapping[target_composite_id] = 'deep'
    
    # 4. Persist Changes to Database
    from tinydb import Query
    WF = Query()
    # We update both 'steps' and 'default_model_mapping'
    engine.repository.db.table('workflows').update({
        "steps": new_steps,
        "default_model_mapping": mapping
    }, WF.id == req.workflow_id)
    
    return {
        "status": "compiled", 
        "composite_step_id": target_composite_id,
        "new_steps": new_steps
    }

    # 1. Identify indices
    indices = sorted([current_steps.index(s) for s in steps_to_fuse])
    first_idx = indices[0]
    
    # 2. Filter out fused steps
    new_steps = [s for s in current_steps if s not in steps_to_fuse]
    
    # 3. Insert target composite step at the position of the first removed step
    new_steps.insert(first_idx, target_composite_id)
    
    # Update Model Mapping
    mapping = wf.get('default_model_mapping', {}).copy()
    
    # Remove old keys
    for step_id in steps_to_fuse:
        if step_id in mapping:
            del mapping[step_id]
            
    # Add new key (Hardcoded DEEP for Panel as per design)
    mapping[target_composite_id] = 'deep'
    
    # 4. Persist Changes to Database
    from tinydb import Query
    WF = Query()
    # We update both 'steps' and 'default_model_mapping'
    engine.repository.db.table('workflows').update({
        "steps": new_steps,
        "default_model_mapping": mapping
    }, WF.id == req.workflow_id)
    
    return {
        "status": "compiled", 
        "composite_step_id": target_composite_id,
        "new_steps": new_steps
    }


