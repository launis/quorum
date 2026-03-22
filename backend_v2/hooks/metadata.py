"""System Metadata Hook for V2 Execution Steps."""

import logging
from datetime import datetime, timezone

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry

logger = logging.getLogger(__name__)

@hook_registry.register(name="inject_step_metadata")
def inject_step_metadata(state: HookState, deps: HookDependencies) -> HookResult:
    """Computes execution metadata including timestamps and initiator information.
    
    This fulfills the V2 requirement for providing 'kello' (timestamp) and 'user' 
    information dynamically to the output dictionary without requiring LLM generation.
    """
    execution_id = state.execution_id or "unknown_execution"
    step_id = state.step_id or "unknown_step"
    workflow_id = state.workflow_id or "unknown_workflow"

    # Try to grab user/initiator from context if it was passed down from the API/Authentication route
    # Fallback to system user if absent
    global_vars = state.global_context_vars or {}
    initiator_id = global_vars.get("_sys_initiator_id", "system")

    metadata = {
        "execution_id": execution_id,
        "workflow_id": workflow_id,
        "step_id": step_id,
        "initiator_id": initiator_id,
        "timestamp_isot": datetime.now(timezone.utc).isoformat(),
        "unix_time": int(datetime.now(timezone.utc).timestamp()),
        "v2_engine": True
    }

    logger.debug(f"[MetadataHook] Injected metadata for step {step_id}")

    return HookResult(success=True, state_delta={
        "step_metadata": metadata,
        # Ensure we always provide a deterministic audit signature
        "_audit_signature": f"{step_id}:{execution_id}:{metadata['unix_time']}"
    })
