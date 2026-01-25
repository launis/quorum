"""Builder Fusion Routes.

Handles validation and compilation of composite steps (Prompt Fusion).
"""

import logging
from typing import Annotated

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from backend.dependencies import EngineDep, RepositoryDep

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Models ---

class CompileRequest(BaseModel):
    """Payload for compiling a sequence of steps into a fusion step."""

    workflow_id: Annotated[str, Field(description="Target workflow ID.")]
    steps: Annotated[list[str], Field(description="List of step IDs to fuse.")]


class ValidationRequest(BaseModel):
    """Payload for validating connection compatibility between steps."""

    source_step: Annotated[str, Field(description="ID of the source step.")]
    target_step: Annotated[str, Field(description="ID of the target step.")]

# --- Endpoints ---

@router.post("/validate", summary="Validate Connection", response_description="Validation result.")
async def validate_connection(request: ValidationRequest, engine: EngineDep, repository: RepositoryDep):
    """Validates connection between two steps based on Agent I/O contracts."""
    try:
        # 1. Resolve Steps
        source_step = await repository.get_step_by_id(request.source_step)
        target_step = await repository.get_step_by_id(request.target_step)

        if not source_step or not target_step:
            return {"valid": False, "reason": "Step(s) not found."}

        # 2. Resolve Agents (via Components)
        src_comp_ref = source_step.get("component")
        tgt_comp_ref = target_step.get("component")

        # Note: get_component needs await
        source_comp = await repository.get_component_by_id(str(src_comp_ref))
        if not source_comp:
            source_comp = await repository.get_component_by_name(str(src_comp_ref))

        target_comp = await repository.get_component_by_id(str(tgt_comp_ref))
        if not target_comp:
            target_comp = await repository.get_component_by_name(str(tgt_comp_ref))

        if not source_comp or not target_comp:
            return {"valid": True, "reason": "Component definitions missing, skipping deep check."}

        src_cls_name = source_comp.get("class_name")
        tgt_cls_name = target_comp.get("class_name")

        src_agent = engine.registry.agents_map.get(str(src_cls_name))
        tgt_agent = engine.registry.agents_map.get(str(tgt_cls_name))

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


@router.post("/compile", summary="Compile Fusion", response_description="Compilation result.")
async def compile_fusion(req: CompileRequest, repository: RepositoryDep):
    """V2: Prompt Fusion Compilation.

    Replaces a sequence of steps with a compatible Composite Step (Panel).
    """
    wf = await repository.get_workflow_by_id(req.workflow_id)
    if not wf:
        from backend.exceptions import ResourceNotFoundError

        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: ID {req.workflow_id}", exc_info=True)
        raise ResourceNotFoundError("Workflow", req.workflow_id, details={"error_code": error_code})

    current_steps = wf.get("steps", [])
    steps_to_fuse = req.steps

    if not all(s in current_steps for s in steps_to_fuse):
        from backend.exceptions import AppException

        error_code = "INVALID_COMPILATION_STEPS_MISSING"
        logger.error(f"{error_code}: Request contains steps not in target workflow.", exc_info=True)
        raise AppException(
            message="Missing steps for fusion",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

    fusing_components = []
    all_step_list = await repository.get_all_steps()
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

    await repository.update_workflow(req.workflow_id, {"steps": new_steps, "default_model_mapping": mapping})

    return {"status": "compiled", "composite_step_id": target_composite_id, "new_steps": new_steps}
