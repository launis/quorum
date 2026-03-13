"""System Metadata Hook for V2 Execution Steps."""

import logging
from datetime import datetime, timezone
from typing import Any

from backend_v2.core.hook_registry import hook_registry

logger = logging.getLogger(__name__)

@hook_registry.register(name="inject_step_metadata")
def inject_step_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Computes execution metadata including timestamps and initiator information.
    
    This fulfills the V2 requirement for providing 'kello' (timestamp) and 'user' 
    information dynamically to the output dictionary without requiring LLM generation.
    """
    execution_id = data.get("_sys_execution_id", "unknown_execution")
    step_id = data.get("_sys_step_id", "unknown_step")
    workflow_id = data.get("_sys_workflow_id", "unknown_workflow")

    # Try to grab user/initiator from context if it was passed down from the API/Authentication route
    # Fallback to system user if absent
    initiator_id = data.get("_sys_initiator_id", "system")

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

    return {
        "step_metadata": metadata,
        # Ensure we always provide a deterministic audit signature
        "_audit_signature": f"{step_id}:{execution_id}:{metadata['unix_time']}"
    }
