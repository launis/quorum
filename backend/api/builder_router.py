from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
import logging
import uuid
import copy
from datetime import datetime
from tinydb import Query

from backend.dependencies import get_engine
from backend.core.engine import WorkflowEngine

router = APIRouter(
    prefix="/builder",
    tags=["Builder"],
    responses={404: {"description": "Resource Not Found"}},
)

logger = logging.getLogger(__name__)

# --- Models ---

class WorkflowCreateRequest(BaseModel):
    name: Annotated[str, Field(description="The unique name for the new workflow.")]
    description: Annotated[Optional[str], Field(description="A description of the workflow's purpose.")] = None
    steps: Annotated[List[str], Field(description="An ordered list of step IDs to include in the workflow.")]
    ui_schema: Annotated[Optional[Dict[str, Any]], Field(description="Layout coordinates for the frontend canvas.")] = None
    default_model_mapping: Annotated[Optional[Dict[str, str]], Field(description="Map of Step IDs to Model Strategy keys.")] = None

class WorkflowUpdateRequest(BaseModel):
    name: Annotated[Optional[str], Field(description="New name.")] = None
    description: Annotated[Optional[str], Field(description="New description.")] = None
    steps: Annotated[Optional[List[str]], Field(description="New ordered list of steps.")] = None
    ui_schema: Annotated[Optional[Dict[str, Any]], Field(description="New layout data.")] = None
    default_model_mapping: Annotated[Optional[Dict[str, str]], Field(description="New model mapping.")] = None

class CopyWorkflowRequest(BaseModel):
    new_name: Annotated[str, Field(description="The name for the copied workflow.")]

class ValidationRequest(BaseModel):
    source_step: Annotated[str, Field(description="The upstream step ID.")]
    target_step: Annotated[str, Field(description="The downstream step ID.")]

class WorkflowTemplate(BaseModel):
    name: Annotated[str, Field(description="Name of the template.")]
    description: Annotated[str, Field(description="Description.")] = ""
    steps: Annotated[List[str], Field(description="Empty step list.")] = []
    default_model_mapping: Annotated[Dict[str, str], Field(description="Empty map.")] = {}
    ui_schema: Annotated[Dict[str, Any], Field(description="Default UI schema.")] = {"nodes": []}

class CompileRequest(BaseModel):
    workflow_id: Annotated[str, Field(description="The ID of the workflow to modifying.")]
    steps: Annotated[List[str], Field(description="Values of step IDs to fuse.")]

class StepUpdateRequest(BaseModel):
    name: Annotated[Optional[str], Field(description="New display name.")] = None
    execution_config: Annotated[Optional[Dict[str, Any]], Field(description="Updated internal config (prompts, etc).")] = None


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

@router.get(
    "/config/agents", 
    summary="List Agent Class Metadata",
    response_description="A list of agent definitions including I/O contracts."
)
async def get_available_agents(engine: WorkflowEngine = Depends(get_engine)):
    """
    Returns metadata for all registered agents, used for the Builder Toolbox.

    Args:
        engine (WorkflowEngine): Dependency.

    Returns:
        List[dict]: Agent metadata objects.
    """
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
                "outputs": []
            }
            agents_meta.append(meta)
                
        return agents_meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/workflows", 
    summary="List Workflows",
    response_description="All Workflows."
)
async def list_workflows(engine: WorkflowEngine = Depends(get_engine)):
    """List all workflows for the dashboard."""
    return engine.repository.get_all_workflows()

@router.post(
    "/workflows", 
    summary="Create Workflow",
    response_description="Created workflow data."
)
async def create_workflow(request: WorkflowCreateRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    Create a new workflow with a generated short ID.
    """
    try:
        new_id = str(uuid.uuid4()).split('-')[0] # Short ID
        workflow_data = {
            "id": f"wf_{new_id}", 
            "name": request.name,
            "description": request.description or "",
            "steps": request.steps,
            "default_model_mapping": request.default_model_mapping or {},
            "ui_schema": request.ui_schema or {}, 
            "created_at": datetime.now().isoformat()
        }
        
        engine.repository.db.table('workflows').insert(workflow_data)
        return workflow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/workflows/{workflow_id}", 
    summary="Get Workflow",
    response_description="Workflow details."
)
async def get_workflow(workflow_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """Get details of a specific workflow."""
    wf = engine.repository.get_workflow_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf

@router.put(
    "/workflows/{workflow_id}", 
    summary="Update Workflow",
    response_description="Updated workflow."
)
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
    
    Layout = Query()
    engine.repository.db.table('workflows').update(update_data, Layout.id == workflow_id)
    
    return {**wf, **update_data}

@router.delete(
    "/workflows/{workflow_id}", 
    summary="Delete Workflow",
    response_description="Deletion status and cleaned up orphans."
)
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

@router.post(
    "/workflows/{workflow_id}/copy", 
    summary="Copy Workflow",
    response_description="The new workflow object."
)
async def copy_workflow(workflow_id: str, request: CopyWorkflowRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    Deep Copy a workflow structure (Shallow copy of steps).
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
    
    clean_wf = dict(new_wf)
    
    try:
        engine.repository.db.table('workflows').insert(clean_wf)
        return clean_wf
    except Exception as e:
        logger.error(f"Copy workflow failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Copy failed: {str(e)}")

@router.post(
    "/validate", 
    summary="Validate Connection",
    response_description="Validation result."
)
async def validate_connection(request: ValidationRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    Validates connection between two steps based on Agent I/O contracts.
    """
    try:
        # 1. Resolve Steps
        source_step = engine.repository.get_step_by_id(request.source_step)
        target_step = engine.repository.get_step_by_id(request.target_step)
        
        if not source_step or not target_step:
             return {"valid": False, "reason": "Step(s) not found."}
             
        # 2. Resolve Agents (via Components)
        src_comp_ref = source_step.get('component')
        tgt_comp_ref = target_step.get('component')
        
        source_comp = engine.repository.get_component_by_id(src_comp_ref) or engine.repository.get_component_by_name(src_comp_ref)
        target_comp = engine.repository.get_component_by_id(tgt_comp_ref) or engine.repository.get_component_by_name(tgt_comp_ref)
        
        if not source_comp or not target_comp:
             return {"valid": True, "reason": "Component definitions missing, skipping deep check."}

        src_cls_name = source_comp.get('class_name')
        tgt_cls_name = target_comp.get('class_name')
        
        src_agent = engine.registry.agents_map.get(src_cls_name)
        tgt_agent = engine.registry.agents_map.get(tgt_cls_name)
        
        if not src_agent or not tgt_agent:
             return {"valid": True, "reason": "Agent implementation not found in registry."}
             
        # 3. Check Contracts
        required = getattr(tgt_agent, "REQUIRES_KEYS", [])
        produced = getattr(src_agent, "PRODUCES_KEYS", [])
        
        missing = [req for req in required if req not in produced]
        
        if missing and required:
            msg = f"⚠️ Potential Schema Mismatch: Target requires {missing}. Source produces {produced}. Ensure dependencies exist upstream."
            return {"valid": True, "reason": msg}

        return {"valid": True, "reason": "Connection Compatible."}

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {"valid": True, "reason": f"Validation error: {str(e)}"}


# --- V2: Step Configuration ---

@router.get(
    "/steps/{step_id}", 
    summary="Get Step Details",
    response_description="Step configuration."
)
async def get_step_details(step_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """V2: Get full configuration of a step."""
    step = engine.repository.get_step_by_id(step_id)
    if not step:
         raise HTTPException(status_code=404, detail="Step not found")
    return step

@router.put(
    "/steps/{step_id}", 
    summary="Update Step",
    response_description="Updated step."
)
async def update_step(step_id: str, request: StepUpdateRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    V2: Update a step configuration.
    WARNING: This modifies the global step definition.
    """
    step = engine.repository.get_step_by_id(step_id)
    if not step:
         raise HTTPException(status_code=404, detail="Step not found")
         
    update_data = {}
    if request.name is not None: update_data['name'] = request.name
    if request.execution_config is not None: update_data['execution_config'] = request.execution_config
    
    Step = Query()
    engine.repository.db.table('steps').update(update_data, Step.id == step_id)
    
    return {**step, **update_data}

@router.post(
    "/steps/clone", 
    summary="Clone Step",
    response_description="The new custom step config."
)
async def clone_step(source_step_id: str = Body(..., embed=True), engine: WorkflowEngine = Depends(get_engine)):
    """
    V2: Clone a step to a new Custom Step (Copy-on-Write).
    """
    step = engine.repository.get_step_by_id(source_step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Source step not found")
        
    new_id = f"{source_step_id}_custom_{uuid.uuid4().hex[:6]}"
    new_step = copy.deepcopy(step)
    new_step['id'] = new_id
    new_step['name'] = f"{step.get('name')} (Custom)"
    
    clean_step = dict(new_step)
    
    engine.repository.db.table('steps').insert(clean_step)
    
    return clean_step

@router.get(
    "/utils/generate-id", 
    summary="Generate ID",
    response_description="A unique ID string."
)
async def generate_id(prefix: str = "custom_step"):
    """Generates a unique ID with optional prefix."""
    return {"id": f"{prefix}_{uuid.uuid4().hex[:6]}"}

@router.get(
    "/config/template", 
    summary="Get Template",
    response_description="Empty workflow template."
)
async def get_workflow_template():
    """Returns a valid empty workflow template."""
    return WorkflowTemplate(
        name="New Workflow",
        description="",
        steps=[],
        default_model_mapping={},
        ui_schema={"nodes": []}
    )

@router.get(
    "/config/fusion-rules", 
    summary="Get Fusion Rules",
    response_description="List of fusion rules."
)
async def get_fusion_rules(engine: WorkflowEngine = Depends(get_engine)):
    """
    Returns validation rules for prompt fusion.
    """
    rules = []
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

@router.get(
    "/config/prompt-types", 
    summary="Get Prompt Types",
    response_description="List of allowed types."
)
async def get_prompt_types():
    """Returns list of component types that can be used as prompts."""
    return ["prompt", "mandate", "rule", "header", "instruction"]

@router.post(
    "/compile", 
    summary="Compile Fusion",
    response_description="Compilation result."
)
async def compile_fusion(req: CompileRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    V2: Prompt Fusion Compilation.
    Replaces a sequence of steps with a compatible Composite Step (Panel).
    """
    wf = engine.repository.get_workflow_by_id(req.workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    current_steps = wf.get('steps', [])
    steps_to_fuse = req.steps
    
    if not all(s in current_steps for s in steps_to_fuse):
        raise HTTPException(status_code=400, detail="One or more steps not found in workflow")

    fusing_components = []
    step_map = {s['id']: s for s in engine.repository.db.table('steps').all()}
    
    for sid in steps_to_fuse:
        s_def = step_map.get(sid)
        if s_def:
            fusing_components.append(s_def.get('component'))
    
    target_composite_id = "step_panel" 
    valid_fusion = False
    
    all_steps = step_map.values()
    for s in all_steps:
        if 'fusion_info' in s:
            allowed = set(s['fusion_info'].get('replaces_components', []))
            if fusing_components and all(comp in allowed for comp in fusing_components):
                target_composite_id = s['id']
                valid_fusion = True
                break
    
    if not valid_fusion:
        logger.warning(f"Fusion validation weak for steps: {steps_to_fuse}. Defaulting to step_panel.")
    
    indices = sorted([current_steps.index(s) for s in steps_to_fuse])
    first_idx = indices[0]
    
    new_steps = [s for s in current_steps if s not in steps_to_fuse]
    new_steps.insert(first_idx, target_composite_id)
    
    mapping = wf.get('default_model_mapping', {}).copy()
    for step_id in steps_to_fuse:
        if step_id in mapping:
            del mapping[step_id]
            
    mapping[target_composite_id] = 'deep'
    
    WF = Query()
    engine.repository.db.table('workflows').update({
        "steps": new_steps,
        "default_model_mapping": mapping
    }, WF.id == req.workflow_id)
    
    return {
        "status": "compiled", 
        "composite_step_id": target_composite_id,
        "new_steps": new_steps
    }
