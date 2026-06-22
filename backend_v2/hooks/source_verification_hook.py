"""Hook for verifying source claims before DAG execution.

This hook extracts explicit source claims from input documents and uses
the Tavily AI search client to verify them against live web data.
"""

import logging

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.services.source_verification_service import SourceVerificationService

logger = logging.getLogger(__name__)


async def source_verification_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Extracts and verifies source claims from text inputs.

    Args:
        state: The current execution state.
        deps: Dependencies for execution.

    Returns:
        HookResult with state_delta containing verified_sources.
    """
    if not state.inputs:
        return HookResult(success=True, state_delta={})

    text_content = ""
    for val in state.inputs.values():
        if isinstance(val, str):
            text_content += val + "\\n\\n"

    if not text_content.strip():
        return HookResult(success=True, state_delta={})

    try:
        service = SourceVerificationService()
        result = await service.run_full_verification(text_content)

        return HookResult(
            success=True,
            state_delta={"verified_sources": result.model_dump(mode="json")},
        )
    except Exception as e:
        logger.error(f"Source verification hook failed: {e}", exc_info=True)
        raise
