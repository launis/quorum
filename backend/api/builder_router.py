"""API Router for Workflow Builder and Management.

This module provides endpoints for creating, updating, copying, and validating
workflows and steps, including the Builder UI toolbox and fusion logic.
"""

import copy
import logging
import uuid
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from backend.dependencies import CurrentUserDep, EngineDep
from backend.models.auth import UserRole

router = APIRouter(
    prefix="/builder",
    tags=["Builder"],
    responses={404: {"description": "Resource Not Found"}},
)

logger = logging.getLogger(__name__)


class BuilderWorkflowCreateRequest(BaseModel):
    """Payload for creating a new workflow.

    Attributes:
        name (str): The name of the workflow.
        description (Optional[str]): Detailed description.
        steps (list[str]): List of step IDs to include.
        default_model_mapping (Optional[dict]): Map of step IDs to model strategies.
        ui_schema (Optional[dict]): Frontend layout metadata.
        is_public (bool): Visibility flag (System Root only).
    """

    name: Annotated[str, Field(description="Name of the new workflow.")]
    description: Annotated[str | None, Field(description="Optional description.")] = None
    steps: Annotated[list[str], Field(description="List of step IDs.")] = []
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Initial model mapping.")] = {}
    ui_schema: Annotated[dict[str, Any] | None, Field(description="UI Layout metadata.")] = {}
    is_public: Annotated[bool, Field(description="If True, visible to all tenants (System Only).")] = False


class WorkflowUpdateRequest(BaseModel):
    name: Annotated[str | None, Field(description="New name.")] = None
    description: Annotated[str | None, Field(description="New description.")] = None
    steps: Annotated[list[str] | None, Field(description="New step sequence.")] = None
    ui_schema: Annotated[dict[str, Any] | None, Field(description="New UI metadata.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Updated model mapping.")] = None
    is_public: Annotated[bool | None, Field(description="Update visibility.")] = None


class StepUpdateRequest(BaseModel):
    name: Annotated[str | None, Field(description="New step name.")] = None
    execution_config: Annotated[dict[str, Any] | None, Field(description="Updated execution config.")] = None


class CopyWorkflowRequest(BaseModel):
    new_name: Annotated[str, Field(description="Name for the copy.")]


class CustomStepCreateRequest(BaseModel):
    component_type: Annotated[str, Field(description="Base component type (e.g. 'Judge', 'Analyst').")]
    name_hint: Annotated[str | None, Field(description="Optional name override.")] = None


class CompileRequest(BaseModel):
    workflow_id: Annotated[str, Field(description="Target workflow ID.")]
    steps: Annotated[list[str], Field(description="List of step IDs to fuse.")]


class WorkflowTemplate(BaseModel):
    name: str
    description: str
    steps: list[str]
    default_model_mapping: dict[str, str]
    ui_schema: dict[str, Any]


class ValidationRequest(BaseModel):
    source_step: Annotated[str, Field(description="ID of the source step.")]
    target_step: Annotated[str, Field(description="ID of the target step.")]


# --- Endpoints ---


@router.get(
    "/config/agents",
    summary="List Agent Class Metadata",
    response_description="A list of agent definitions including I/O contracts.",
)
async def get_available_agents(engine: EngineDep):
    """Returns metadata for all registered agents, used for the Builder Toolbox.

    Args:
        engine (EngineDep): Dependency.

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
                "outputs": [],
            }
            agents_meta.append(meta)

        return agents_meta
    except Exception as e:
        logger.error(f"Failed to list agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows", summary="List Workflows", response_description="All Workflows.")
async def list_workflows(engine: EngineDep, current_user: CurrentUserDep):
    """List all workflows visible to the current user.

    Args:
        engine (EngineDep): Workflow engine dependency.
        current_user (CurrentUserDep): The requesting user.

    Returns:
        list[dict]: A list of workflow definitions.
    """
    return await engine.repository.get_all_workflows(
        organization_id=current_user.organization_id, role=current_user.role
    )


@router.get("/steps", summary="List Steps", response_description="All Steps.")
async def list_steps(engine: EngineDep):
    """List all available steps.

    Returns:
        list[dict]: A list of step definitions.
    """
    return await engine.repository.get_all_steps()


@router.post("/workflows", summary="Create Workflow", response_description="Created workflow data.")
async def create_workflow(request: BuilderWorkflowCreateRequest, engine: EngineDep, current_user: CurrentUserDep):
    """Create a new workflow.

    Args:
        request (BuilderWorkflowCreateRequest): Workflow definition.
        engine (EngineDep): Engine dependency.
        current_user (CurrentUserDep): Requesting user (ROOT/MANAGER).

    Returns:
        dict: The created workflow object.

    Raises:
        HTTPException: If permission denied (403) or creation fails (500).
    """
    # 1. RBAC Check
    if current_user.role not in [UserRole.ROOT, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Only ROOT or MANAGER can create workflows.")

    # 2. Org Assignment
    # If ROOT, they "own" the system org (usually).
    # If MANAGER, forced to their org.
    target_org = current_user.organization_id or "system"  # Default to system if root has None

    # 3. Visibility Check
    is_public_val = False
    if request.is_public:
        if current_user.role != UserRole.ROOT:
            raise HTTPException(status_code=403, detail="Only ROOT can make workflows public.")
        is_public_val = True

    try:
        new_id = str(uuid.uuid4()).split("-")[0]  # Short ID
        workflow_data = {
            "id": f"wf_{new_id}",
            "name": request.name,
            "description": request.description or "",
            "steps": request.steps,
            "default_model_mapping": request.default_model_mapping or {},
            "ui_schema": request.ui_schema or {},
            "created_at": datetime.now().isoformat(),
            "organization_id": target_org,
            "is_public": is_public_val,
        }

        await engine.repository.create_workflow(workflow_data)
        return workflow_data
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", summary="Get Workflow", response_description="Workflow details.")
async def get_workflow(workflow_id: str, engine: EngineDep):
    """Get details of a specific workflow.

    Args:
        workflow_id (str): The UUID of the workflow.
        engine (EngineDep): Engine dependency.

    Returns:
        dict: The workflow definition.

    Raises:
        HTTPException: If not found (404).
    """
    wf = await engine.repository.get_workflow_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.put("/workflows/{workflow_id}", summary="Update Workflow", response_description="Updated workflow.")
async def update_workflow(
    workflow_id: str, request: WorkflowUpdateRequest, engine: EngineDep, current_user: CurrentUserDep
):
    """Update an existing workflow.

    Args:
        workflow_id (str): The UUID of the workflow to update.
        request (WorkflowUpdateRequest): Fields to update.
        engine (EngineDep): Engine dependency.
        current_user (CurrentUserDep): Requesting user.

    Returns:
        dict: The updated workflow object.

    Raises:
        HTTPException: If not found (404) or permission denied (403).
    """
    wf = await engine.repository.get_workflow_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Permission Check
    wf_org = wf.get("organization_id")
    is_system_wf = wf_org is None or wf_org == "system"

    if is_system_wf:
        if current_user.role != UserRole.ROOT:
            raise HTTPException(status_code=403, detail="Only ROOT can modify System Workflows.")
    else:
        # Tenant Workflow
        if current_user.role not in [UserRole.ROOT, UserRole.MANAGER]:
            raise HTTPException(status_code=403, detail="Insufficient role to modify workflow.")
        if wf_org != current_user.organization_id and current_user.role != UserRole.ROOT:
            raise HTTPException(status_code=403, detail="Cannot modify other organization's workflow.")

    # Public Check
    if request.is_public is not None and request.is_public != wf.get("is_public"):
        if current_user.role != UserRole.ROOT:
            raise HTTPException(status_code=403, detail="Only ROOT can change visibility.")

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.description is not None:
        update_data["description"] = request.description
    if request.steps is not None:
        update_data["steps"] = request.steps
    if request.ui_schema is not None:
        update_data["ui_schema"] = request.ui_schema
    if request.default_model_mapping is not None:
        update_data["default_model_mapping"] = request.default_model_mapping
    if request.is_public is not None:
        update_data["is_public"] = request.is_public

    update_data["updated_at"] = datetime.now().isoformat()

    # Ensure Model Mapping Integrity
    final_steps = update_data.get("steps", wf.get("steps", []))
    final_mapping = update_data.get("default_model_mapping", wf.get("default_model_mapping", {})).copy()

    mapping_modified = False
    for s in final_steps:
        if s not in final_mapping:
            final_mapping[s] = "fast"
            mapping_modified = True

    if mapping_modified:
        # If input didn't provide mapping but we modified it based on steps, save it.
        update_data["default_model_mapping"] = final_mapping

    await engine.repository.update_workflow(workflow_id, update_data)

    return {**wf, **update_data}


@router.delete(
    "/workflows/{workflow_id}",
    summary="Delete Workflow",
    response_description="Deletion status and cleaned up orphans.",
)
async def delete_workflow(workflow_id: str, engine: EngineDep, current_user: CurrentUserDep):
    """Delete a workflow AND its orphan steps (Garbage Collection).

    Args:
        workflow_id (str): UUID of the workflow.
        engine (EngineDep): Engine dependency.
        current_user (CurrentUserDep): Requesting user.

    Returns:
        dict: Status and list of deleted orphan steps.

    Raises:
        HTTPException: If permission denied (403).
    """
    wf = await engine.repository.get_workflow_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Permission Check
    wf_org = wf.get("organization_id")
    is_system_wf = wf_org is None or wf_org == "system"

    if is_system_wf:
        if current_user.role != UserRole.ROOT:
            raise HTTPException(status_code=403, detail="Only ROOT can delete System Workflows.")
    else:
        if current_user.role not in [UserRole.ROOT, UserRole.MANAGER]:
            raise HTTPException(status_code=403, detail="Insufficient role to delete workflow.")
        if wf_org != current_user.organization_id and current_user.role != UserRole.ROOT:
            raise HTTPException(status_code=403, detail="Cannot delete other organization's workflow.")

    # 0. Integrity Check: Execution History
    # Prevent deleting workflows that have audit history.
    all_execs = await engine.repository.get_all_executions()
    related_execs = [e for e in all_execs if e.get("workflow_id") == workflow_id]

    if related_execs:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot delete workflow '{workflow_id}' because it has {len(related_execs)} execution record(s). "
                "Archive it or delete executions first."
            ),
        )

    # 1. Identify Orphan Steps
    # 1. Identify Orphan Steps
    # Helper must be updated to await or we fetch data here
    # _get_orphan_steps is sync in helper. We should inline logic or make helper async.
    # For now, let's fetch all workflows here to pass to helper logic (refactoring helper is safer)

    # Actually, let's make a local async helper or just fetch data
    orphans = []
    all_wfs = await engine.repository.get_all_workflows()

    target_steps = set(wf.get("steps", []))
    used_elsewhere = set()
    for w in all_wfs:
        if w["id"] == workflow_id:
            continue
        for s in w.get("steps", []):
            used_elsewhere.add(s)
    orphans = list(target_steps - used_elsewhere)

    # 2. Delete Workflow
    await engine.repository.delete_workflow(workflow_id)

    # 3. Delete Orphans
    deleted_steps = []
    for step_id in orphans:
        await engine.repository.delete_step(step_id)
        deleted_steps.append(step_id)

    logger.info(f"Deleted workflow {workflow_id} and orphan steps: {deleted_steps}")

    return {"status": "deleted", "deleted_steps": deleted_steps}


@router.post("/workflows/{workflow_id}/copy", summary="Copy Workflow", response_description="The new workflow object.")
async def copy_workflow(workflow_id: str, request: CopyWorkflowRequest, engine: EngineDep):
    """Deep Copy a workflow structure (Shallow copy of steps)."""
    original = await engine.repository.get_workflow_by_id(workflow_id)
    if not original:
        raise HTTPException(status_code=404, detail="Workflow not found")

    new_id = f"{original['id']}_copy_{uuid.uuid4().hex[:4]}"

    new_wf = copy.deepcopy(original)
    new_wf["id"] = new_id
    new_wf["name"] = request.new_name
    new_wf["created_at"] = datetime.now().isoformat()
    if "updated_at" in new_wf:
        del new_wf["updated_at"]

    clean_wf = dict(new_wf)

    try:
        await engine.repository.create_workflow(clean_wf)
        return clean_wf
    except Exception as e:
        logger.error(f"Copy workflow failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Copy failed: {str(e)}")


@router.post("/validate", summary="Validate Connection", response_description="Validation result.")
async def validate_connection(request: ValidationRequest, engine: EngineDep):
    """Validates connection between two steps based on Agent I/O contracts.

    Args:
        request (ValidationRequest): Source and Target step IDs.
        engine (EngineDep): Engine dependency.

    Returns:
        dict: Validation result (valid: bool, reason: str).
    """
    try:
        # 1. Resolve Steps
        source_step = await engine.repository.get_step_by_id(request.source_step)
        target_step = await engine.repository.get_step_by_id(request.target_step)

        if not source_step or not target_step:
            return {"valid": False, "reason": "Step(s) not found."}

        # 2. Resolve Agents (via Components)
        src_comp_ref = source_step.get("component")
        tgt_comp_ref = target_step.get("component")

        # Note: get_component needs await
        source_comp = await engine.repository.get_component_by_id(src_comp_ref)
        if not source_comp:
            source_comp = await engine.repository.get_component_by_name(src_comp_ref)

        target_comp = await engine.repository.get_component_by_id(tgt_comp_ref)
        if not target_comp:
            target_comp = await engine.repository.get_component_by_name(tgt_comp_ref)

        if not source_comp or not target_comp:
            return {"valid": True, "reason": "Component definitions missing, skipping deep check."}

        src_cls_name = source_comp.get("class_name")
        tgt_cls_name = target_comp.get("class_name")

        src_agent = engine.registry.agents_map.get(src_cls_name)
        tgt_agent = engine.registry.agents_map.get(tgt_cls_name)

        if not src_agent or not tgt_agent:
            return {"valid": True, "reason": "Agent implementation not found in registry."}

        # 3. Check Contracts
        required = getattr(tgt_agent, "REQUIRES_KEYS", [])
        produced = getattr(src_agent, "PRODUCES_KEYS", [])

        missing = [req for req in required if req not in produced]

        if missing and required:
            msg = (
                f"⚠️ Potential Schema Mismatch: Target requires {missing}. Source produces {produced}. "
                "Ensure dependencies exist upstream."
            )
            return {"valid": True, "reason": msg}

        return {"valid": True, "reason": "Connection Compatible."}

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return {"valid": True, "reason": f"Validation error: {str(e)}"}


# --- V2: Step Configuration ---


@router.get("/steps/{step_id}", summary="Get Step Details", response_description="Step configuration.")
async def get_step_details(step_id: str, engine: EngineDep):
    """V2: Get full configuration of a step.

    Args:
        step_id (str): The UUID of the step.
        engine (EngineDep): Engine dependency.

    Returns:
        dict: The step configuration.
    """
    step = await engine.repository.get_step_by_id(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return step


@router.put("/steps/{step_id}", summary="Update Step", response_description="Updated step.")
async def update_step(step_id: str, request: StepUpdateRequest, engine: EngineDep):
    """V2: Update a step configuration.
    WARNING: This modifies the global step definition.
    """
    step = await engine.repository.get_step_by_id(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.execution_config is not None:
        update_data["execution_config"] = request.execution_config

    if request.execution_config is not None:
        update_data["execution_config"] = request.execution_config

    await engine.repository.update_step(step_id, update_data)

    return {**step, **update_data}


@router.post("/steps/clone", summary="Clone Step", response_description="The new custom step config.")
async def clone_step(engine: EngineDep, source_step_id: str = Body(..., embed=True)):
    """V2: Clone a step to a new Custom Step (Copy-on-Write)."""
    step = await engine.repository.get_step_by_id(source_step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Source step not found")

    new_id = f"{source_step_id}_custom_{uuid.uuid4().hex[:6]}"
    new_step = copy.deepcopy(step)
    new_step["id"] = new_id
    new_step["name"] = f"{step.get('name')} (Custom)"

    clean_step = dict(new_step)

    await engine.repository.create_step(clean_step)

    return clean_step


@router.post(
    "/steps/create-custom", summary="Create Custom Step", response_description="The newly created custom step."
)
async def create_custom_step(req: CustomStepCreateRequest, engine: EngineDep):
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
        await engine.repository.create_step(new_step)
        return new_step
    except Exception as e:
        logger.error(f"Failed to create custom step: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/utils/generate-id", summary="Generate ID", response_description="A unique ID string.")
async def generate_id(prefix: str = "custom_step"):
    """Generates a unique ID with optional prefix."""
    return {"id": f"{prefix}_{uuid.uuid4().hex[:6]}"}


@router.get("/config/template", summary="Get Template", response_description="Empty workflow template.")
async def get_workflow_template():
    """Returns a valid empty workflow template."""
    return WorkflowTemplate(
        name="New Workflow", description="", steps=[], default_model_mapping={}, ui_schema={"nodes": []}
    )


@router.get("/config/fusion-rules", summary="Get Fusion Rules", response_description="List of fusion rules.")
async def get_fusion_rules(engine: EngineDep):
    """Returns validation rules for prompt fusion."""
    rules = []
    all_steps = await engine.repository.get_all_steps()
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


@router.post("/compile", summary="Compile Fusion", response_description="Compilation result.")
async def compile_fusion(req: CompileRequest, engine: EngineDep):
    """V2: Prompt Fusion Compilation.
    Replaces a sequence of steps with a compatible Composite Step (Panel).
    """
    wf = await engine.repository.get_workflow_by_id(req.workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    current_steps = wf.get("steps", [])
    steps_to_fuse = req.steps

    if not all(s in current_steps for s in steps_to_fuse):
        raise HTTPException(status_code=400, detail="One or more steps not found in workflow")

    fusing_components = []
    all_step_list = await engine.repository.get_all_steps()
    step_map = {s["id"]: s for s in all_step_list}

    for sid in steps_to_fuse:
        s_def = step_map.get(sid)
        if s_def:
            fusing_components.append(s_def.get("component"))

    target_composite_id = "step_panel"
    valid_fusion = False

    all_steps = step_map.values()
    for s in all_steps:
        if "fusion_info" in s:
            allowed = set(s["fusion_info"].get("replaces_components", []))
            if fusing_components and all(comp in allowed for comp in fusing_components):
                target_composite_id = s["id"]
                valid_fusion = True
                break

    if not valid_fusion:
        logger.warning(f"Fusion validation weak for steps: {steps_to_fuse}. Defaulting to step_panel.")

    indices = sorted([current_steps.index(s) for s in steps_to_fuse])
    first_idx = indices[0]

    new_steps = [s for s in current_steps if s not in steps_to_fuse]
    new_steps.insert(first_idx, target_composite_id)

    mapping = wf.get("default_model_mapping", {}).copy()
    for step_id in steps_to_fuse:
        if step_id in mapping:
            del mapping[step_id]

    mapping[target_composite_id] = "deep"

    await engine.repository.update_workflow(req.workflow_id, {"steps": new_steps, "default_model_mapping": mapping})

    return {"status": "compiled", "composite_step_id": target_composite_id, "new_steps": new_steps}
